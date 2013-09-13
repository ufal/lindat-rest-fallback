# coding=utf-8
# See main file for licence
""" One plugin. """
import codecs
import os

from applications import plugin
import utils


class cesilko(plugin):
    """
        Cesilko wrapper
    """
    exposed_uri = "/cesilko"
    temp_dir = "/home/cesilko/tmp/"
    tr_script = "/var/www/cgi-bin/cesilko/run.csh"

    api_translate = "translate"
    api_key_data = "data"

    def version(self):
        """ Cesilko version """
        # TODO should be retrieved from cesilko itself
        return { "version": "todo version" }

    def execute(self, *args, **kwargs):
        """
            Execute the application.
        """
        if not cesilko.api_translate in args:
            return self._failed( detail="Invalid API - no method with such a name" )
        if 0 == len(kwargs.get(cesilko.api_key_data, "")):
            return self._failed( detail="missing data parameter" )

        try:
            #(input_f, input_fname_rel) = self._get_temp_file()
            (input_f, input_fname_rel) = self._get_unique_file(enc='iso-8859-2')
            expected_output_file_name = input_f.name + ".SK.out"
            text = kwargs[cesilko.api_key_data]

            with input_f as fout:
                fout.write( text.encode('utf-8') )
                print 'Written input data to file ' + fout.name 

            cmd = "%s %s" % (cesilko.tr_script, input_fname_rel)
            self.log( "Cesilko ran: [%s]", cmd )
            retcode, stdout, stderr = utils.run( cmd )
            output_exists = os.path.exists(expected_output_file_name)
            if 0 == retcode and os.path.exists(expected_output_file_name):
                with codecs.open(expected_output_file_name, 'rb', 'iso-8859-2') as fin:
                    translated_text = fin.read()
                    translated_text_uni = translated_text.encode('iso-8859-2').decode('utf-8')
                    return {
                        "input": text,
                        "result": translated_text_uni
                    }
            else:
                return self._failed( detail="retcode:%d, exists(%s)=%s, stdout=%s, stderr=%s, cmd=%s" % (retcode,  expected_output_file_name, output_exists, stdout, stderr, cmd) )

        except Exception, e:
            return self._failed( detail=utils.uni(e) )

    #
    #

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
