from django.core.files.storage import FileSystemStorage
from PIL import Image
import uuid
import subprocess
import os


def compress_and_temporary_store_jpeg(file,
                                      temporary_local_file_path,
                                      images_loss_mode=2,
                                      images_quality=70,
                                      minimum_resized_image_size=1500):
    """
    :param (required) file: A bytes like file django object (an instance of 'django.core.files.uploadedfile.InMemoryUploadedFile'
                           or 'django.core.files.uploadedfile.TemporaryUploadedFileobject').

    :param (required) temporary_local_file_path: The local path where we are going to temporary save the file.

    :param (optional) images_loss_mode: The loss mode for the image compression
                                        Accepted values :
                                           1: low loss
                                           2: extremely low loss (recommended for websites except for picture
                                           specialized websites)
                                           3: no loss

    :param (optional) images_quality: A value between 0 and 100.
                                      Recommended range : 65 to 95
                                      Recommended quality for websites (except for picture specialized websites) : 70

    :param (optional) minimum_resized_image_size: If the size (the highest value between the height and the width of
                                                  the image) of an image after optimization is lower than the value of
                                                  the 'minimum_resized_image_size' variable value, set the size with
                                                  this same value.
                                                  Note that if the size of the image is natively lower than the value of
                                                  this variable, the image will not be resized.
    """

    picture = Image.open(file)

    picture_width, picture_height = picture.size
    reference_size = picture_width if picture_width > picture_height else picture_height
    max_size = None

    if int(images_loss_mode) == 1:
        if reference_size >= minimum_resized_image_size / 0.4:
            max_size = reference_size * 0.4

        else:
            max_size = minimum_resized_image_size

    elif int(images_loss_mode) == 2:
        if reference_size >= minimum_resized_image_size / 0.6:
            max_size = reference_size * 0.6

        else:
            max_size = minimum_resized_image_size

    elif int(images_loss_mode) == 3:
        if reference_size >= minimum_resized_image_size / 0.8:
            max_size = reference_size * 0.8

        else:
            max_size = minimum_resized_image_size

    ratio = (max_size / picture_width, max_size / picture_height)

    picture.thumbnail((picture_width * ratio[0], picture_height * ratio[1]),
                      Image.ANTIALIAS)
    picture.save(temporary_local_file_path,
                                "JPEG",
                                optimize=True,
                                quality=images_quality)

    picture.close()


def compress_and_temporary_store_png(file,
                                     temporary_local_file_path,
                                     images_loss_mode=2,
                                     images_quality=70,
                                     minimum_resized_image_size=1500):
    """
    :param (required) file: A bytes like file django object (an instance of 'django.core.files.uploadedfile.InMemoryUploadedFile'
                           or 'django.core.files.uploadedfile.TemporaryUploadedFileobject').

    :param (required) temporary_local_file_path: The local path where we are going to temporary save the file.

    :param (optional) images_loss_mode: The loss mode for the image compression
                                        Accepted values :
                                           1: low loss
                                           2: extremely low loss (recommended for websites except for picture
                                           specialized websites)
                                           3: no loss

    :param (optional) images_quality: A value between 0 and 100.
                                      Recommended range : 65 to 95
                                      Recommended quality for websites (except for picture specialized websites) : 70

    :param (optional) minimum_resized_image_size: If the size (the highest value between the height and the width of
                                                  the image) of an image after optimization is lower than the value of
                                                  the 'minimum_resized_image_size' variable value, set the size with
                                                  this same value.
                                                  Note that if the size of the image is natively lower than the value of
                                                  this variable, the image will not be resized.
    """

    picture = Image.open(file)

    picture_width, picture_height = picture.size
    reference_size = picture_width if picture_width > picture_height else picture_height
    max_size = None

    if int(images_loss_mode) == 1:
        if reference_size >= minimum_resized_image_size / 0.6:
            max_size = reference_size * 0.6

        else:
            max_size = minimum_resized_image_size

    elif int(images_loss_mode) == 2:
        if reference_size >= minimum_resized_image_size / 0.8:
            max_size = reference_size * 0.8

        else:
            max_size = minimum_resized_image_size

    elif int(images_loss_mode) == 3:
        if reference_size >= minimum_resized_image_size:
            max_size = reference_size

        else:
            max_size = minimum_resized_image_size

    ratio = (max_size / picture_width, max_size / picture_height)

    picture.thumbnail((picture_width * ratio[0], picture_height * ratio[1]),
                      Image.ANTIALIAS)
    picture.convert("RGB").save(temporary_local_file_path,
                                "JPEG",
                                optimize=True,
                                quality=images_quality)

    picture.close()


def compress_and_temporary_store_pdf(file,
                                     temporary_local_file_path,
                                     pdf_loss_mode=3):
    """
    :param (required) file: A bytes like file django object (an instance of 'django.core.files.uploadedfile.InMemoryUploadedFile'
                            or 'django.core.files.uploadedfile.TemporaryUploadedFileobject').

    :param (required) temporary_local_file_path:  The local path where we are going to temporary save the file.

    :param (optional) pdf_loss_mode: The loss mode for the image compression
                                     Accepted values :
                                        1: prepress (no loss)
                                        2: printer (no loss)
                                        3: ebook (extremely low loss) (recommended)
                                        4: screen (visible loss)

   """

    quality = {
        1: '/prepress',
        2: '/printer',
        3: '/ebook',
        4: '/screen'
    }

    temporary_local_file_path_list = temporary_local_file_path.split("/")

    not_compressed_temporary_file_fullname = "notcomp_" + temporary_local_file_path_list[-1]

    temporary_local_file_path_list.pop(-1)
    temporary_local_folder = "/".join(temporary_local_file_path_list) + "/"

    not_compressed_temporary_local_file_path = temporary_local_folder + not_compressed_temporary_file_fullname

    fs = FileSystemStorage(location=temporary_local_folder)
    fs.save(not_compressed_temporary_file_fullname, file)

    subprocess.call(['gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
                     '-dPDFSETTINGS={}'.format(quality[pdf_loss_mode]),
                     '-dNOPAUSE', '-dQUIET', '-dBATCH',
                     '-sOutputFile={}'.format(temporary_local_file_path),
                     not_compressed_temporary_local_file_path]
                    )

    os.remove(not_compressed_temporary_local_file_path)


def compress_and_temporary_store_svg(file, temporary_local_file_path):
    temporary_local_file_path_list = temporary_local_file_path.split("/")

    not_compressed_temporary_file_fullname = "notcomp_" + temporary_local_file_path_list[-1]

    temporary_local_file_path_list.pop(-1)
    temporary_local_folder = "/".join(temporary_local_file_path_list) + "/"

    not_compressed_temporary_local_file_path = temporary_local_folder + not_compressed_temporary_file_fullname

    fs = FileSystemStorage(location=temporary_local_folder)
    fs.save(not_compressed_temporary_file_fullname, file)

    subprocess.call(f"scour -i {not_compressed_temporary_local_file_path} -o {temporary_local_file_path} --enable-viewboxing --enable-id-stripping --enable-comment-stripping --shorten-ids --indent=none", shell=True)

    os.remove(not_compressed_temporary_local_file_path)


def compress_file_and_build_paths(django_file_object,
                                  images_loss_mode=2,
                                  images_quality=70,
                                  minimum_resized_image_size=1500,
                                  pdf_loss_mode=3):
    """

    :param (required) django_file_object: The django file object (an instance of 'django.core.files.uploadedfile.InMemoryUploadedFile'
                                          or 'django.core.files.uploadedfile.TemporaryUploadedFileobject').

    :param (optional) images_loss_mode: The loss mode for the image compression
                                        Accepted values :
                                           1: low loss
                                           2: extremely low loss (recommended for websites except for picture
                                              specialized websites)
                                           3: no loss

    :param (optional) images_quality: A value between 0 and 100.
                                      Recommended range : 65 to 95
                                      Recommended quality for websites (except for picture specialized websites) : 70

    :param (optional) minimum_resized_image_size: If the size (the highest value between the height and the width of
                                                  the image) of an image after optimization is lower than the value of
                                                  the 'minimum_resized_image_size' variable value, set the size with
                                                  this same value.
                                                  Note that if the size of the image is natively lower than the value of
                                                  this variable, the image will not be resized.

    :param (optional) pdf_loss_mode: The loss mode for the image compression
                                 Accepted values :
                                    1: prepress (no loss)
                                    2: printer (no loss)
                                    3: ebook (extremely low loss) (recommended)
                                    4: screen (visible loss)

    :return (temporary_local_file_path, remote_file_path) :
                - temporary_local_file_path = The local path where is temporary saved the file.
                - remote_file_path = The remote path (on the SFTP server) where we are going to store the file)
    """
    django_file_object_dict = django_file_object.__dict__
    file = django_file_object_dict["file"]
    file_name = uuid.uuid4().hex

    content_type = django_file_object_dict["content_type"]

    temporary_local_file_path = None
    remote_file_path = None

    # JPEG IMAGES OPTIMIZATION :
    if content_type == "image/jpeg":
        file_fullname = file_name + ".jpeg"

        temporary_local_file_path = f"/tmp/{file_fullname}"
        remote_file_path = f"/www/staticfiles/content/img/{file_fullname}"

        compress_and_temporary_store_jpeg(file=file,
                                          temporary_local_file_path=temporary_local_file_path,
                                          images_loss_mode=images_loss_mode,
                                          images_quality=images_quality,
                                          minimum_resized_image_size=minimum_resized_image_size)

    # PNG IMAGES OPTIMIZATION :
    elif content_type == "image/png":

        file_fullname = file_name + ".jpeg"

        temporary_local_file_path = f"/tmp/{file_fullname}"
        remote_file_path = f"/www/staticfiles/content/img/{file_fullname}"

        compress_and_temporary_store_png(file=file,
                                         temporary_local_file_path=temporary_local_file_path,
                                         images_loss_mode=images_loss_mode,
                                         images_quality=images_quality,
                                         minimum_resized_image_size=minimum_resized_image_size)

    # PDF OPTIMIZATION :
    elif content_type == "application/pdf":

        file_fullname = file_name + ".pdf"

        temporary_local_file_path = f"/tmp/{file_fullname}"
        remote_file_path = f"/www/staticfiles/content/pdf/{file_fullname}"

        compress_and_temporary_store_pdf(file=file,
                                         temporary_local_file_path=temporary_local_file_path,
                                         pdf_loss_mode=pdf_loss_mode)

    elif content_type == "image/svg+xml":

        file_fullname = file_name + ".svg"

        temporary_local_file_path = f"/tmp/{file_fullname}"
        remote_file_path = f"/www/staticfiles/content/svg/{file_fullname}"

        compress_and_temporary_store_svg(file=file,
                                         temporary_local_file_path=temporary_local_file_path)

    else:
        print("THIS CONTENT TYPE IS NOT SUPPORTED, today, the sftp module can just handle .svg, .png, .jpg, .jpeg and .pdf files.")
        return None

    return (temporary_local_file_path, remote_file_path)

