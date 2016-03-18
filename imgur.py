from imgurpython import ImgurClient

class Imgur():

    def __init__(self, _id, _secret):
    	self._id = _id
    	self._secret = _secret
    	self.client = ImgurClient(self._id, self._secret)

    def Image_Upload(self, path):
    	return self.client.upload_from_path(path)

