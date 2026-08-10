import cv2


def calculate_blur_score(
    image_path: str,
) -> float:
    """
    Calculate image sharpness using
    the variance of the Laplacian.

    Higher score generally indicates
    a sharper image.
    """

    image = cv2.imread(
        image_path,
        cv2.IMREAD_GRAYSCALE,
    )

    if image is None:
        raise ValueError(
            f"Unable to read image: {image_path}"
        )

    laplacian = cv2.Laplacian(
        image,
        cv2.CV_64F,
    )

    return float(
        laplacian.var()
    )