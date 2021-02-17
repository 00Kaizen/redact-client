import pathlib
import pytest

from io import BytesIO
from typing import IO

from redact_client.data_models import ServiceType, OutputType, JobLabels
from redact_client.redact_instance import RedactInstance


@pytest.fixture(scope='module')
def redact(redact_url) -> RedactInstance:
    return RedactInstance.create(service=ServiceType.blur, out_type=OutputType.images, redact_url=redact_url)


@pytest.fixture(scope='module')  # Re-use the initial labels for every test
def some_image() -> IO:
    img_path = pathlib.Path(__file__).parent.parent.joinpath('resources/obama.jpg')
    with open(img_path, 'rb') as f:
        yield f


@pytest.fixture(scope='module')  # Re-use the initial labels for every test
def some_image_labels(redact, some_image) -> JobLabels:
    some_image.seek(0)
    job = redact.start_job(file=some_image)
    labels = job.wait_until_finished().get_labels()
    assert len(labels.frames[0].faces) == 1
    return labels


@pytest.mark.timeout(10)
class TestCustomLabels:
    """
    Test different formats to provide custom_labels: as JSON string, file, BytesIO, or JobLabels object.
    """

    def test_labels_of_result_equal_custom_labels_from_str(self, redact, some_image, some_image_labels):

        # GIVEN the labels of an anonymized image
        # WHEN the labels (as string) are used again as custom_labels
        custom_labels = some_image_labels.json()
        some_image.seek(0)
        new_labels = redact.start_job(some_image, custom_labels=custom_labels).wait_until_finished().get_labels()

        # THEN the labels of the result are the same as the custom labels
        assert new_labels == some_image_labels

    def test_labels_of_result_equal_custom_labels_from_object(self, redact, some_image, some_image_labels):

        # GIVEN the labels of an anonymized image
        # WHEN these labels (as JobLabels object) are used again as custom_labels
        some_image.seek(0)
        new_labels = redact.start_job(some_image, custom_labels=some_image_labels).wait_until_finished().get_labels()

        # THEN the labels of the result are the same as the custom labels
        assert new_labels == some_image_labels

    def test_labels_of_result_equal_custom_labels_from_file(self, redact, some_image, some_image_labels, tmp_path):

        # GIVEN the labels of an anonymized image (stored in a file)
        labels_path = tmp_path.joinpath('labels.json')
        with open(str(labels_path), 'w') as f:
            f.write(some_image_labels.json())

        # WHEN these label file is used again as custom_labels
        some_image.seek(0)
        with open(str(labels_path), 'rb') as f:
            new_labels = redact.start_job(some_image, custom_labels=f).wait_until_finished().get_labels()

        # THEN the labels of the result are the same as the custom labels
        assert new_labels == some_image_labels

    def test_labels_of_result_equal_custom_labels_from_mem_file(self, redact, some_image, some_image_labels):

        # GIVEN the labels of an anonymized image
        # WHEN these labels are used again as custom_labels
        custom_labels = BytesIO(some_image_labels.json().encode())
        some_image.seek(0)
        new_labels = redact.start_job(some_image, custom_labels=custom_labels).wait_until_finished().get_labels()

        # THEN the labels of the result are the same as the custom labels
        assert new_labels == some_image_labels
