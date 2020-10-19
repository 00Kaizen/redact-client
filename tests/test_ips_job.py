import io
import os
import pytest

from PIL import Image

from ips_data_models import IPSJobState
from ips_job import JobArguments, IPSJob, IPSServiceTypes, IPSInputOutputTypes


@pytest.fixture
def ips_url():
    return os.environ['IPS_URL']


class TestIPSJob:

    def test_wait_for_status_completed(self, ips_url, test_image):

        # GIVEN a running IPS instance and a test image

        # WHEN a job is posted
        job_args = JobArguments(service=IPSServiceTypes.dnat, out_type=IPSInputOutputTypes.images)
        job = IPSJob(file=test_image, job_args=job_args, ips_url=ips_url)

        # THEN the job finishes after a while
        assert job.start().wait_until_finished().get_status().state == IPSJobState.finished

    def test_download_result(self, ips_url, test_image):

        # GIVEN a running IPS instance amd a test image
        img = Image.open(test_image)
        test_image.seek(0)

        # WHEN a job is posted
        job_args = JobArguments(service=IPSServiceTypes.dnat, out_type=IPSInputOutputTypes.images)
        job = IPSJob(file=test_image, job_args=job_args, ips_url=ips_url)

        # THEN its result can be downloaded and has the same size as the input image
        anonymized_raw = job.start().wait_until_finished().download_result()
        anonymized_img = Image.open(io.BytesIO(anonymized_raw))
        assert anonymized_img.size == img.size
