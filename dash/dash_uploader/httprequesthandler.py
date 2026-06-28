import logging
import os
import shutil
import time
import traceback

from flask import request
from flask import abort

logger = logging.getLogger(__name__)


def get_chunk_name(uploaded_filename, chunk_number):
    return uploaded_filename + "_part_%03d" % chunk_number


class BaseHttpRequestHandler:
    def __init__(self, server, upload_folder, use_upload_id):
        """
        Parameters
        ----------
        server: flask.Flask
            The flask server instance
        upload_folder: str
            The folder to use for uploads
        use_upload_id: bool
            Determines if the uploads are put into
            folders defined by a "upload id" (upload_id).
            If True, uploads will be put into `folder`/<upload_id>/;
            that is, every user (for example with different
            session id) will use their own folder. If False,
            all files from all sessions are uploaded into
            same folder (not recommended).

        """
        self.server = server
        self.upload_folder = upload_folder
        self.use_upload_id = use_upload_id

    def post(self):
        try:
            return self._post()
        except Exception:
            logger.error(traceback.format_exc())

    def _post(self):
        resumableTotalChunks = request.form.get("resumableTotalChunks", type=int)
        resumableChunkNumber = request.form.get(
            "resumableChunkNumber", default=1, type=int
        )
        resumableFilename = request.form.get(
            "resumableFilename", default="error", type=str
        )
        resumableIdentifier = request.form.get(
            "resumableIdentifier", default="error", type=str
        )
        upload_id = request.form.get("upload_id", default="", type=str)

        # get the chunk data
        chunk_data = request.files["file"]

        # make our temp directory
        temp_root = self.get_temp_root(upload_id)
        temp_dir = os.path.join(temp_root, resumableIdentifier)
        if not os.path.isdir(temp_dir):
            os.makedirs(temp_dir)

        # save the chunk data
        chunk_name = get_chunk_name(resumableFilename, resumableChunkNumber)
        chunk_file = os.path.join(temp_dir, chunk_name)

        # make a lock file
        lock_file_path = os.path.join(
            temp_dir, ".lock_{:d}".format(resumableChunkNumber)
        )

        with open(lock_file_path, "a"):
            os.utime(lock_file_path, None)
        chunk_data.save(chunk_file)
        os.unlink(lock_file_path)

        # check if the upload is complete
        chunk_paths = [
            os.path.join(temp_dir, get_chunk_name(resumableFilename, x))
            for x in range(1, resumableTotalChunks + 1)
        ]
        upload_complete = all([os.path.exists(p) for p in chunk_paths])

        # combine all the chunks to create the final file
        if upload_complete:

            # Make sure all files are finished writing
            # but do not wait forever..
            tried = 0
            while any(
                [
                    os.path.isfile(os.path.join(temp_dir, ".lock_{:d}".format(chunk)))
                    for chunk in range(1, resumableTotalChunks + 1)
                ]
            ):
                tried += 1
                if tried >= 5:
                    logger.error("Error uploading files with temp_dir: %s.", temp_dir)
                    raise Exception("Error uploading files with temp_dir: " + temp_dir)
                time.sleep(1)

            # Make sure some other chunk didn't trigger file reconstruction
            target_file_name = os.path.join(temp_root, resumableFilename)
            if os.path.exists(target_file_name):
                logger.info("File %s exists already. Overwriting..", target_file_name)
                os.unlink(target_file_name)

            with open(target_file_name, "ab") as target_file:
                for p in chunk_paths:
                    with open(p, "rb") as stored_chunk_file:
                        target_file.write(stored_chunk_file.read())
            self.server.logger.debug("File saved to: %s", target_file_name)
            shutil.rmtree(temp_dir)

        return resumableFilename

    def get(self):
        try:
            return self._get()
        except Exception:
            logger.error(traceback.format_exc())

    def _get(self):
        # resumable.js uses a GET request to check if it uploaded the file already.
        # https://github.com/23/resumable.js#handling-get-or-test-requests
        # TODO: Since testChunks is set to false, this seems to be permanently disabled.
        #       Should this be removed altogether?

        resumableIdentifier = request.args.get("resumableIdentifier", type=str)
        resumableFilename = request.args.get("resumableFilename", type=str)
        resumableChunkNumber = request.args.get("resumableChunkNumber", type=int)

        upload_id = request.args.get("upload_id", default="", type=str)

        if not (resumableIdentifier and resumableFilename and resumableChunkNumber):
            # Parameters are missing or invalid
            abort(500, "Parameter error")

        # chunk folder path based on the parameters
        temp_dir = os.path.join(self.get_temp_root(upload_id), resumableIdentifier)

        # chunk path based on the parameters
        chunk_file = os.path.join(
            temp_dir, get_chunk_name(resumableFilename, resumableChunkNumber)
        )
        self.server.logger.debug("Getting chunk: %s", chunk_file)

        if os.path.isfile(chunk_file):
            # Let resumable.js know this chunk already exists
            return "OK"
        else:
            # Let resumable.js know this chunk does not exists
            # and needs to be uploaded
            abort(404, "Not found")

    def get_temp_root(self, upload_id):
        return (
            os.path.join(self.upload_folder, upload_id)
            if self.use_upload_id
            else self.upload_folder
        )


class HttpRequestHandler(BaseHttpRequestHandler):
    # You may use the flask.request
    # and flask.session inside the methods of this
    # class when needed.
    def __init__(self, *args, **kwargs):  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)

    def post_before(self):
        pass

    def post(self):
        self.post_before()
        returnvalue = super().post()
        self.post_after()
        return returnvalue

    def post_after(self):
        pass

    def get_before(self):
        pass

    def get(self):
        self.get_before()
        returnvalue = super().get()
        self.get_after()
        return returnvalue

    def get_after(self):
        pass
