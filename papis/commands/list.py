import papis
import os
import sys
import papis.utils
from . import Command
import papis.downloaders.utils


class List(Command):
    def init(self):
        """TODO: Docstring for init.

        :subparser: TODO
        :returns: TODO

        """
        list_parser = self.parser.add_parser(
            "list",
            help="List documents from a given library"
        )

        list_parser.add_argument(
            "document",
            help="Document search",
            default="",
            nargs="?",
            action="store"
        )

        list_parser.add_argument(
            "-i",
            "--info",
            help="Show the info file name associated with the document",
            default=False,
            action="store_true"
        )

        list_parser.add_argument(
            "-f",
            "--file",
            help="Show the file name associated with the document",
            action="store_true"
        )

        list_parser.add_argument(
            "-d",
            "--dir",
            help="Show the folder name associated with the document",
            default=True,
            action="store_true"
        )

        list_parser.add_argument(
            "-p",
            "--pick",
            help="Pick the document instead of listing everything",
            action="store_true"
        )

        list_parser.add_argument(
            "--downloaders",
            help="List available downloaders",
            action="store_true"
        )

    def main(self, config, args):
        """
        Main action if the command is triggered

        :config: User configuration
        :args: CLI user arguments
        :returns: TODO

        """
        if args.downloaders:
            for downloader in \
            papis.downloaders.utils.getAvailableDownloaders():
                print(downloader)
            sys.exit(0)
        documentsDir = os.path.expanduser(config[args.lib]["dir"])
        self.logger.debug("Using directory %s" % documentsDir)
        documentSearch = args.document
        documents = papis.utils.getFilteredDocuments(
            documentsDir,
            documentSearch
        )
        if args.pick:
            documents = [self.pick(documents, config)]
        for document in documents:
            if args.file:
                for f in document.getFiles():
                    print(f)
            elif args.dir:
                print(document.getMainFolder())
            elif args.info:
                print(
                    os.path.join(
                        document.getMainFolder(),
                        document.getInfoFile()
                    )
                )
            else:
                print(document)
