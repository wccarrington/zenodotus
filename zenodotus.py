#! /usr/bin/env python3

import hashlib
import sys
import os


def hashfile(filename):
    f = open(filename, 'rb')
    sha = hashlib.new('sha256')
    sha.update(f.read())
    return sha.hexdigest()


# An index is a directory, with a store file, and one or more tag files
# the store file has lines of form "[sha256 hash] [file name]"
# the tag file's name is the tag, and have a list of hashes that have that tag
class Index:
    STORE_FILENAME = 'storefile'
    def __init__(self, dirname):
        self.dirname = dirname
        self.readindex()

    def readindex(self):
        self.files = {}
        self.hashes = {}
        self.tags = {}
        infile = open(self.dirname + os.sep + self.STORE_FILENAME)
        for line in infile:
            shahash, filename = (l.strip() for l in line.split(None, 1))
            self.insert_file_with_hash(shahash, filename)
        for tagfile in os.listdir(self.dirname):
            if tagfile != self.STORE_FILENAME:
                self.tags[tagfile] = [l.strip() for l in open(os.path.join(self.dirname, tagfile)).readlines()]

    def writeindex(self):
        outfile = open(self.dirname + os.sep + self.STORE_FILENAME, 'w')
        for filename, shahash in self.files.items():
            outfile.write(shahash + ' ' + filename + '\n')
        outfile.close()

    def insert(self, filename):
        shahash =  hashfile(filename)
        self.insert_file_with_hash(shahash, filename)

    def insert_file_with_hash(self, shahash, filename):
        self.files[filename] = shahash
        self.hashes[shahash] = filename

    def dump(self):
        for filename, shahash in self.files.items():
            print(filename, shahash)
            for tag, filehashes in self.tags.items():
                if shahash in filehashes:
                    print(tag)
            print()


def main():
    if len(sys.argv) < 2:
        print('Must supply an argument')
        return
    if sys.argv[1] == 'insert':
        filename = sys.argv[2]
        if filename[0] != '/':
            filename = os.path.abspath(filename)
        print('Inserting file:', filename)
        index = Index('zenoindex')
        index.insert(filename)
        index.writeindex()
    elif sys.argv[1] == 'dump':
        index = Index('zenoindex')
        index.dump()
    else:
        print('Unknown option:', sys.argv[1])


if __name__ == '__main__':
    main()
