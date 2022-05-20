try:
    from app.camera import Camera
except ModuleNotFoundError:
    from app.camera2 import Camera

def test_camera_initialization():
    cam = Camera()
    assert isinstance(cam, Camera)