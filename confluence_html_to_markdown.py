import sys, errno, os
import re
import subprocess
import shutil
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--input_dir', default='.', help = "Directory of the input htmls")
parser.add_argument('--output_dir', default='./output', help = "Directory of the output markdown files")


def is_path_exist(pathname):
    return os.path.exists(pathname)

def is_path_creatable(pathname):
    dirname = os.path.dirname(pathname)
    return os.access(dirname, os.W_OK)

# from Django
def get_valid_filename(s):
    """
    Return the given string converted to a string that can be used for a clean
    filename. Remove leading and trailing spaces; convert other spaces to
    underscores; and remove anything that is not an alphanumeric, dash,
    underscore, or dot.
    >>> get_valid_filename("john's portrait in 2004.jpg")
    'johns_portrait_in_2004.jpg'
    """
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)
    

class Processor():
    def __init__(self, **kwargs):
        self.options = {
            'intput' : '',
            'output' : ''
        }
        self.options.update(kwargs)
        self.input_dir = self.options.get('input', '')
        self.output_dir = self.options.get('output', '')
        self.output_img_dir = Processor.get_output_img_path(self.output_dir)

    @classmethod
    def get_valid_input_path(cls, pathname):
        if not is_path_exist(pathname):
            return os.getcwd()
        return pathname

    @classmethod
    def get_output_img_path(cls, dir):
        return os.path.join(dir, 'images')

    @classmethod
    def get_valid_output_path(cls, pathname):
        try:
            if not is_path_exist(pathname):
                if is_path_creatable(pathname):
                    os.makedirs(pathname)
                    os.makedirs(Processor.get_output_img_path(pathname))
                    return pathname, Processor.get_output_img_path(pathname)
                else:
                    output = os.path.join(os.getcwd(), 'markdown_output')
                    if not is_path_exist(output):
                        os.makedirs(output)
                        os.makedirs(Processor.get_output_img_path(output))
                    return output, Processor.get_output_img_path(output)
            elif not is_path_exist(Processor.get_output_img_path(pathname)):
                os.makedirs(Processor.get_output_img_path(pathname))
            return pathname, Processor.get_output_img_path(pathname)
        except OSError:
            print("[ERROR] output dir invalid. {:s}".format(pathname))
            return '', ''
    
    def syntax_modify_image(self, raw_str):
        from_pattern1 = re.compile('<img src=\"([a-zA-Z0-9_]+\/){2}')
        to_string1 = '![](/images/'
        from_pattern2 = re.compile('\" class=.+?\/>')
        to_string2 = ')'
        mod_str = re.sub(from_pattern1, to_string1, raw_str)
        mod_str = re.sub(from_pattern2, to_string2, mod_str)
        return mod_str
    
    def syntax_remove_attachments(self, raw_str):
        pattern = re.compile('Attachments:\n-+(\n)*(.*\n)*.*')
        mod_str = re.sub(pattern, '', raw_str)
        return mod_str

    def syntax_append_hexo_header(self, raw_str, title):
        mod_str = '---\ntitle: ' + title + '\ndate: 2018-01-01 00:00:00\ntags: []\ncategories: \ndescription: \n---\n' + raw_str
        return mod_str

    def processing(self):
        # check input and output path
        self.input_dir = Processor.get_valid_input_path(self.input_dir)
        self.output_dir, self.output_img_dir = Processor.get_valid_output_path(self.output_dir)
        if (self.output_dir == ''):
            return

        # start processing
        self.traverse_folder(self.input_dir)
        print('[INFO] done.')
    
    def traverse_folder(self, dir):
        for entry in os.scandir(dir):
            if not entry.name.startswith('.') and entry.is_file():
                self.convert_html(entry.path, entry.name)
            elif entry.is_dir():
                self.traverse_folder(entry.path)

    def convert_html(self, dir, name):
        try:
            if(name.endswith('.html')):
                print('[INFO] processing {:s}'.format(name))
                # get file content
                whole_text = ''
                input_file = dir
                with open(input_file, mode = 'r', encoding = 'utf-8') as file:
                    whole_text = file.read()
                # get file title
                title_regex = "<title>.*</title>"
                title = re.findall(title_regex, whole_text)[0].replace('<title>', '').replace('</title>', '')
                title = get_valid_filename(title)
                output_file = os.path.join(self.output_dir, title+'.md')
                # convert file
                result = subprocess.call('pandoc -f html -t markdown_github -o \"' + output_file + "\" \"" + input_file + "\"")
                # images
                images_regex = '<a href=\"attachments/.*\">'
                images = [img.replace('<a href=\"','').replace('\">', '') for img in re.findall(images_regex, whole_text)]
                for img in images:
                    src = os.path.join(self.input_dir, img)
                    dest = os.path.join(self.output_img_dir, img.split('/')[-1])
                    shutil.copyfile(src, dest)
                # change syntax in md file
                md_str = ''
                with open(output_file, mode = 'r', encoding = 'utf-8') as md_file:
                    md_str = md_file.read()

                md_str = self.syntax_modify_image(md_str)
                md_str = self.syntax_remove_attachments(md_str)
                md_str = self.syntax_append_hexo_header(md_str, title)

                with open(output_file, mode = 'w', encoding = 'utf-8') as w_file:
                    w_file.write(md_str)
                print('[INFO] complete {:s}.'.format(name))
        except OSError:
            print('[ERROR] failed to open file {:s} or write to {:s}'.format(name, self.output_dir))
            return
        except:
            print('[ERROR] convert {:s} failed.'.format(name))
            return

if __name__ == "__main__":
    args = parser.parse_args()
    input_dir = args.input_dir
    output_dir = args.output_dir
    pro = Processor(input = input_dir, output = output_dir)
    pro.processing()
