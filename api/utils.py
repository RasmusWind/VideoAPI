import re
import os
import random


range_re = re.compile(r"bytes\s*=\s*(\d+)\s*-\s*(\d*)", re.I)


class RangeFileWrapper(object):
    def __init__(self, filelike, blksize=1024, offset=0, length=None):
        self.filelike = filelike
        self.filelike.seek(offset, os.SEEK_SET)
        self.remaining = length
        self.blksize = blksize

    def close(self):
        if hasattr(self.filelike, "close"):
            self.filelike.close()

    def __iter__(self):
        return self

    def __next__(self):
        if self.remaining is None:
            # If remaining is None, we're reading the entire file.
            data = self.filelike.read(self.blksize)
            if data:
                return data
            raise StopIteration()
        else:
            if self.remaining <= 0:
                raise StopIteration()
            data = self.filelike.read(min(self.remaining, self.blksize))
            if not data:
                raise StopIteration()
            self.remaining -= len(data)
            return data


def findNextRandomVid(oldPath):
    video_dir = "media/video_uploads"
    file_set = []
    for dir_, _, files in os.walk(video_dir):
        for file_name in files:
            rel_dir = os.path.relpath(dir_, video_dir)
            rel_file = os.path.join(rel_dir, file_name)
            if oldPath != rel_file:
                file_set.append(rel_file)
    if len(file_set) == 0:
        return None
    random_num = random.randrange(0, len(file_set))
    return file_set[random_num]
