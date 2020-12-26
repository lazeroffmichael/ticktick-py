class TagsManager:

    def __init__(self, client_class):
        self._client = client_class
        self.access_token = self._client.access_token

    def create(self):
        pass

    def update(self):
        pass

    def delete(self, tag_name: str):
        """
        Deletes the tag with the name if it exists
        :param tag_name:
        :return:
        """
        # Determine if the tag exists
        tag_obj = self.get_etag(name=tag_name, search_key='tags')
        tag_obj = self.get_by_etag(tag_obj[0])
        if not tag_obj:
            raise ValueError(f"Tag '{tag_name}' Does Not Exist To Delete")

        url = self.BASE_URL + 'tag'
        params = {
            'name': tag_name
        }
        response = self._delete(url, params=params, cookies=self.cookies)
        # Find the tag
        for tag in range(len(self.state['tags'])):
            if self.state['tags'][tag]['etag'] == tag_obj['etag']:
                del self.state['tags'][tag]
                break

        return tag_obj['etag']