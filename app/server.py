import logging, os, sys

from rasa_sdk import utils
from rasa_sdk.endpoint import create_argument_parser, run

GIT_FOLDER = '/app/git'
# GIT_FOLDER = './'

def main_from_args(args):
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("matplotlib").setLevel(logging.WARN)

    utils.configure_colored_logging(args.loglevel)
    utils.update_sanic_log_level()

    # args.actions = args.actions or DEFAULT_ACTIONS_PATH

    git_dirs = os.listdir(GIT_FOLDER)
    # git_dirs.remove('ssh_files')

    git_dirs_ = []

    for x in git_dirs:
        try:
            git_dirs_.append(int(x))
        except:
            pass


    print((git_dirs_))

    sys.path.append(GIT_FOLDER + '/' + str(git_dirs_[0]) + '/actions')
    
    # sys.path.append('./actions')
    args.actions = 'actions'

    run(
        args.actions,
        args.port,
        args.cors,
        args.ssl_certificate,
        args.ssl_keyfile,
        args.ssl_password,
        args.auto_reload,
    )


def main():
    # Running as standalone python application
    arg_parser = create_argument_parser()
    cmdline_args = arg_parser.parse_args()

    main_from_args(cmdline_args)


if __name__ == "__main__":
    main()
