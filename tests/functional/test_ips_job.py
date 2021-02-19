import io
import pytest

from PIL import Image

from redact_client.data_models import JobState, RedactResponseError


class TestRedactJob:

    def test_wait_for_status_completed(self, job):
        # GIVEN an Redact job
        # WHEN a job is started
        # THEN the job finishes after a while
        assert job.wait_until_finished().get_status().state == JobState.finished

    def test_download_result(self, any_img_redact_inst, some_image):

        # GIVEN an image and the corresponding Redact job
        job = any_img_redact_inst.start_job(some_image)

        # WHEN the job is finished and the result downloaded
        job_result = job.wait_until_finished().download_result()

        # THEN the response has the right media type
        assert job_result.media_type.startswith('image')

        # AND it has the same size as the input image
        anonymized_img = Image.open(io.BytesIO(job_result.content))
        some_image.seek(0)
        original_img = Image.open(some_image)
        assert anonymized_img.size == original_img.size

    def test_download_labels(self, job):

        # GIVEN an Redact job

        # WHEN a job is started and the labels are downloaded
        job_labels = job.wait_until_finished().get_labels()

        # THEN assert that the result contains the bbox for one face
        assert len(job_labels.frames[0].faces) == 1
        assert len(job_labels.frames[0].faces[0].bounding_box) == 4

    @pytest.mark.timeout(10)
    def test_delete(self, job):

        # GIVEN an Redact job

        # WHEN the job is finished and then deleted
        job.wait_until_finished()
        job.delete()

        # (wait for job to be deleted)
        with pytest.raises(RedactResponseError) as exc_info:
            while True:
                job.get_status()

        # THEN it can not be found anymore
        assert exc_info.value.status_code == 404