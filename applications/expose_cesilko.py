# coding=utf-8
# See main file for licence
""" One plugin. """
import codecs
import os
import re

from applications import plugin
import utils


# noinspection PyBroadException
class cesilko(plugin):
    """
        Cesilko wrapper
    """
    # #######################
    # SOFTWARE INFORMATION
    # #######################
    # Fill the information about the plugin. Please do not change the following 
    # variable names. 
    # 1. software_author   - Author name of the software. Use commas to add more authors.
    # 2. software_version  - Software version number.
    # ########################
    software_author = [u'Jan Hajič', u'Vladislav Kuboň', u'Petr Homola']
    software_version = u'v1.0'
    ##########################

    # #########################
    # PLUGIN SPECIFIC VARIABLES
    # #########################    
    exposed_uri = "/cesilko"
    temp_dir = "/lindat/ufal_apps/cesilko/work/"
    tr_script = "/lindat/ufal_apps/cesilko/run.csh"
    ###########################

    # #########################
    # DEFINE API NAMES
    # #########################
    # Avilable APIs:
    #   1. translate
    #       data - <UTF-8 encoded string>
    # #########################
    api_translate = "translate"
    api_key_data = "data"
    api_key_body = "body"
    ###########################

    def version(self):
        """ Cesilko version """
        return {
            'version': cesilko.software_version,
            'author': cesilko.software_author
        }

    def execute(self, *args, **kwargs):
        """
            Execute the application.
        """
        ret_mime = None

        #self.log( "args [%s], kwargs [%s]", repr(args), repr(kwargs))
        if not cesilko.api_translate in args:
            return self._failed( detail="Invalid API - no method with such a name" )

        # posted raw body
        if cesilko.api_key_body in kwargs:
            ret_mime = "text/plain"
            try:
                kwargs[cesilko.api_key_data] = utils.uni(self.posted_body())
            except:
                return self._failed( detail="invalid posted body" )

        # what should we translate?
        elif 0 == len(kwargs.get(cesilko.api_key_data, "")):
            # hardcoded fallback
            try:
                kwargs[cesilko.api_key_data] = utils.uni(self.posted_body())
                ret_mime = "text/plain"
                self.log( "using fallback mechanism" )
            except:
                return self._failed( detail="missing data parameter" )

        try:
            (input_f, input_fname_rel) = self._get_unique_file(enc='iso-8859-2')
            expected_output_file_name = input_f.name + ".SK.out"
    
            # 1. Input text is in UTF-8
            text = kwargs[cesilko.api_key_data]
            self.log("Received Input Text: %s ", text)
            self.log("Type of the Input: %s", str(type(text)))

            # 2. Convert the UTF-8 encoded text into ISO-8859-2 encoding.
            #    - non ISO-8859-2 characters will be replaced with XML numeric codes
            text_iso_dec = None
            try:
                text_iso = text.encode('iso-8859-2', 'xmlcharrefreplace')
                text_iso_dec = text_iso.decode('iso-8859-2')  # ISO-8859-2 text
                self.log("Replacing the Non ISO-8859-2 Characters Into XML Numeric Entities: %s", text_iso_dec)
            except UnicodeEncodeError:
                self._failed( detail="please supply utf-8 input." )

            with input_f as fout:
                fout.write( text_iso_dec )
                self.log("Written Input Text to File: %s", fout.name)
            cmd = "%s %s %s" % (cesilko.tr_script, input_f.name, expected_output_file_name)
            self.log( "Cesilko ran: [%s]", cmd )
            retcode, stdout, stderr = utils.run( cmd )
            output_exists = os.path.exists(expected_output_file_name)
            if 0 == retcode and os.path.exists(expected_output_file_name):
                with open(expected_output_file_name, 'rb') as fin:
                    translated_text = fin.read()

                    # convert the ISO-8859-2 output text into UTF-8 text
                    #translated_text_dec_utf = translated_text.decode('iso-8859-2').encode('utf-8').decode('utf-8')
                    translated_text_dec_utf = translated_text.decode('iso-8859-2')
                    
                    # remove extra \n\n at the end of the translated text
                    # Cesilko adds this, so it can be removed safely here
                    translated_text_dec_utf = re.sub(r"\n\n$", "", translated_text_dec_utf)
                    
                    # remove extra spaces at the beginning and end
                    translated_text_dec_utf = re.sub(r"(^\s+|\s+$)", "", translated_text_dec_utf)

                    self.log("The UTF-8 Encoded Output: %s", translated_text_dec_utf)

                    ret = {
                        "input": text,
                        "result": translated_text_dec_utf
                    }
                    # special for weblicht
                    if ret_mime is not None:
                        return ret_mime, ret["result"]

                    return ret
            else:
                return self._failed( detail="retcode:%d, exists(%s)=%s, stdout=%s, stderr=%s, cmd=%s" % (
                    retcode, expected_output_file_name, output_exists, stdout, stderr, cmd) )

        except Exception, e:
            return self._failed( detail=utils.uni(e) )

    def _get_temp_file(self):
        """
            Get temp file.
        """
        import tempfile
        tempfile_fid = tempfile.NamedTemporaryFile(
            suffix=".cesilko.input", dir=cesilko.temp_dir, delete=False)
        tempfile_abs_path = tempfile_fid.name
        dir_file = os.path.split(tempfile_abs_path)
        fname = dir_file[1]
        return (tempfile_fid, fname)

    def _get_unique_file(self, enc):
        """
            Returns file handle to a unique file
        """
        import uuid
        uniq_id = str(uuid.uuid4())
        tempfile_name_abs = cesilko.temp_dir + '/' + uniq_id + 'cesilko.input'
        tempfile_name_rel = uniq_id + 'cesilko.input'
        tempfile_fid = codecs.open(tempfile_name_abs,'w', encoding=enc)
        return (tempfile_fid, tempfile_name_rel)

    def _failed(self, **kwargs):
        """
            Return that the conversion failed.
        """
        ret = { "warning": "translation unsuccessful", }
        for k, v in kwargs.iteritems():
            ret[k] = v
        return ret
