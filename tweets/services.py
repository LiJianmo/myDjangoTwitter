from tweets.models import TweetPhoto


class TweetService(object):

    @classmethod
    def create_photos_from_files(cls, tweet, files):
        photos = []
        for index, file in enumerate(files):
            photo = TweetPhoto(
                tweet=tweet,
                user=tweet.user,
                file=file,
                order=index,
            )
            photos.append(photo)
            #批量创建
            #bulk_create()
        TweetPhoto.objects.bulk_create(photos)
