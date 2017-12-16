import filecmp
import os
import shutil
import zipfile

from xx import filex
from xx import iox

from android_studio_translator.tips.tips import Tips
from android_studio_translator.tools import Tools
from android_studio_translator.translator.translation_file import TranslationFile


class JetBrainsTranslator:
    """汉化多个软件"""

    def __init__(self):
        self.work_dir = r'D:\workspace\TranslatorX\JetBrains'
        self.source_dir = self.work_dir + os.path.sep + 'source'
        self.target_dir = self.work_dir + os.path.sep + 'target'

        current_version_list = [
            '3.0.1',
            '2017.3.1'
        ]
        pre_version_list = [
            '3.0',
            '2017.3'
        ]
        software_name_list = [
            'AndroidStudio',
            'IntelliJIDEA',
            'PhpStorm',
            'PyCharm',
            'WebStorm',
        ]

        software_root_dir = r'D:/xx/software/JetBrains/'
        self.software_list = []
        for i in range(len(software_name_list)):
            software_name = software_name_list[i]
            if i >= len(current_version_list):
                # 取最后一个
                version = current_version_list[-1]
            else:
                # 取对应版本
                version = current_version_list[i]
            if i >= len(pre_version_list):
                pre_version = pre_version_list[-1]
            else:
                pre_version = pre_version_list[i]
            software = Software(self.work_dir, software_root_dir + software_name, software_name, version, pre_version)
            self.software_list.append(software)

    def main(self):
        action_list = [
            ['退出', exit],
            ['处理清单文件，整理tips的名称方便翻译', self.process_tips_manifest_file],
            ['检查并补全缺少的tips名', self.check_and_append_tips_name],
            ['将翻译结果的unicode转为中文', self.change_unicode_to_chinese],
            ['处理tips翻译结果为AndroidStudio用', self.process_tips_translation_result],
            ['重命名_zh_CN', self.rename_cn_files],
            ['复制 resources_en.jar', self.iter_software, lambda x: x.copy_resources_en_jar()],
            ['压缩进汉化包', self.iter_software, lambda x: x.zip_translation()],
            ['将汉化包复制到软件目录', self.iter_software, lambda x: x.copy_translation_to_work_dir()],
            ['以下是版本更新时调用的方法------------------', ],
            ['校验版本是否更新', self.iter_software, lambda x: x.validate_version()],
            ['检查 jar 包是否变化', self.iter_software, lambda x: x.compare_jar()],
            ['删除比较 jar 包时的缓存', self.iter_software, lambda x: x.delete_compare_tmp_dir()],
            ['解压 jar 到 source 目录', self.iter_software, lambda x: x.extract_jar_to_source_dir()],
        ]
        iox.choose_action(action_list)

    def process_tips_manifest_file(self):
        tips = Tips()
        project_name_list = os.listdir(self.source_dir)
        for project_name in project_name_list:
            project_path = self.source_dir + os.sep + project_name
            if os.path.isdir(project_path):
                tips_file_path = project_path + os.sep + 'IdeTipsAndTricks' + os.sep + 'IdeTipsAndTricks.xml'
                tips_en_file = filex.get_result_file_name(tips_file_path, '_en', 'properties')
                if os.path.exists(tips_file_path):
                    print('处理 %s' % tips_file_path)
                    tips.process_tips_manifest_file(tips_file_path, tips_en_file)

    def check_and_append_tips_name(self):
        tips = Tips()
        project_name_list = os.listdir(self.source_dir)
        for project_name in project_name_list:
            project_path = self.source_dir + os.sep + project_name
            if os.path.isdir(project_path):
                tips_file_path = project_path + os.sep + 'IdeTipsAndTricks' + os.sep + 'IdeTipsAndTricks.xml'
                tips_en_file = filex.get_result_file_name(tips_file_path, '_en', 'properties')
                if os.path.exists(tips_file_path):
                    print('处理 %s' % tips_file_path)
                    project_tips_path = project_path + os.sep + 'resources_en' + os.sep + 'tips'
                    tips.check_and_append_tips_name(project_tips_path, tips_en_file, tips_en_file)

    def change_unicode_to_chinese(self):
        project_name_list = os.listdir(self.source_dir)
        for project_name in project_name_list:
            project_path = self.target_dir + os.sep + project_name
            if os.path.isdir(project_path):
                tips_dir = project_path + os.sep + 'IdeTipsAndTricks'
                tips_file_path = tips_dir + os.sep + 'IdeTipsAndTricks_en_zh_CN.properties'
                tips_cn_file_path = tips_dir + os.sep + 'IdeTipsAndTricks_cn.properties'
                if os.path.exists(tips_file_path):
                    print('处理 %s' % tips_file_path)
                    Tools.change_unicode_to_chinese(tips_file_path, tips_cn_file_path)

    def process_tips_translation_result(self):
        tips = Tips()
        project_name_list = os.listdir(self.source_dir)
        for project_name in project_name_list:
            project_path = self.target_dir + os.sep + project_name
            if os.path.isdir(project_path):
                tips_dir = project_path + os.sep + 'IdeTipsAndTricks'
                tips_cn_file_path = tips_dir + os.sep + 'IdeTipsAndTricks_cn.properties'
                if os.path.exists(tips_cn_file_path):
                    print('处理 %s' % tips_cn_file_path)
                    project_tips_path = project_path + os.sep + 'resources_en' + os.sep + 'tips'
                    tips.process_tips_translation_result(tips_cn_file_path, project_tips_path,
                                                         Tips.RESULT_TYPE_ANDROID_STUDIO, project_tips_path)

    def rename_cn_files(self):
        project_name_list = os.listdir(self.source_dir)
        for project_name in project_name_list:
            project_path = self.target_dir + os.sep + project_name
            if os.path.isdir(project_path):
                project_messages_path = project_path + os.sep + 'resources_en' + os.sep + 'messages'
                TranslationFile.rename_cn_files(project_messages_path)

    def iter_software(self, callback):
        """对所有软件循环进行操作"""
        for software in self.software_list:
            print()
            callback(software)


class Software:
    def __init__(self, work_dir, path, name=None, version=None, pre_version=None, release_version=1,
                 pre_release_version=1):
        self.work_dir = work_dir
        "汉化包的工作目录"
        self.path = path
        "软件的安装目录"
        base_name = os.path.basename(path)
        if name is None or version is None:
            name_version = base_name.split(' ')
            if len(name_version) > 0:
                if name is None:
                    name = name_version[0]
            if len(name_version) > 1:
                if version is None:
                    version = name_version[1]
        self.name = name
        "软件名"
        self.version = version
        "软件版本"
        self.pre_version = pre_version
        "上一个版本"
        self.release_version = release_version
        "当前软件版本下的汉化包版本，如果需要，可以手动设置，分开设置"
        self.pre_release_version = pre_release_version
        self.en_jar_path = '%s/jars/%s/英文包/%s/%s' % (self.work_dir, self.name, self.version, 'resources_en.jar')
        "软件的英文包"
        self.translation_jar_name = 'resources_cn_%s_%s_r%s.jar' % (self.name, self.version, self.release_version)
        "汉化包言语件名"
        self.translation_jar = '%s/jars/%s/%s' % (self.work_dir, self.name, self.translation_jar_name)
        "汉化包完整路径"

    def copy_resources_en_jar(self):
        """复制 jar"""
        print('处理 %s %s' % (self.name, self.version))
        if not os.path.exists(self.path):
            print('软件目录不存在 %s' % self.path)
            return

        build_file_path = self.path + os.sep + 'build.txt'
        if not os.path.exists(build_file_path):
            print('build.txt 不存在')
            return
        destination_build_file_path = '%s/jars/%s/英文包/%s/%s' % (self.work_dir, self.name, self.version, 'build.txt')
        print('复制 %s 到 %s' % (build_file_path, destination_build_file_path))
        filex.check_and_create_dir(destination_build_file_path)
        shutil.copyfile(build_file_path, destination_build_file_path)

        jar_file_path = self.path + os.sep + 'lib' + os.sep + 'resources_en.jar'
        if not os.path.exists(jar_file_path):
            print('jar 包不存在')
            return
        print('复制 %s 到 %s' % (jar_file_path, self.en_jar_path))
        shutil.copyfile(jar_file_path, self.en_jar_path)

    def zip_translation(self):
        """打包翻译"""
        print('处理 %s %s' % (self.name, self.version))
        translation_dir = '%s/target/%s/resources_en' % (self.work_dir, self.name)
        print('将 %s 压缩到 %s' % (translation_dir, self.translation_jar))
        self.zip(translation_dir, self.translation_jar, self.en_jar_path)

    @staticmethod
    def zip(source_dir, target_jar, source_jar=None):
        if os.path.exists(target_jar):
            os.remove(target_jar)
        if source_jar is not None:
            translation_dir_list = []
            translation_file_list = []
            for root, dirs, files in os.walk(source_dir):
                for dir_name in dirs:
                    path = root + '/' + dir_name
                    translation_dir_list.append(path.replace(source_dir, '').replace('\\', '/').lstrip('/'))
                for file_name in files:
                    path = root + '/' + file_name
                    translation_file_list.append(path.replace(source_dir, '').replace('\\', '/').lstrip('/'))
            print(translation_dir_list)
            print(translation_file_list)
            tmp_dir = os.path.splitext(source_jar)[0]
            if os.path.exists(tmp_dir):
                shutil.rmtree(tmp_dir)
            # 解压仅存在于 source_jar 中的内空
            print('解压缺少的文件')
            with zipfile.ZipFile(source_jar, 'r') as zip_file:
                for name in zip_file.namelist():
                    for translation_dir in translation_dir_list:
                        if name.startswith(translation_dir):
                            if name not in translation_file_list:
                                # print('翻译文件中缺少 %s ，解压缩' % name)
                                zip_file.extract(name, tmp_dir)
            print('压缩缺少的文件')
            ZipTools.zip_jar(tmp_dir, target_jar)
            # 删除
            print('删除临时文件 %s' % tmp_dir)
            if os.path.exists(tmp_dir):
                shutil.rmtree(tmp_dir)
        # 压缩翻译内容
        ZipTools.zip_jar(source_dir, target_jar)

    def copy_translation_to_work_dir(self):
        """复制汉化包到工作目录"""
        jar_file_path = self.path + os.sep + 'lib' + os.sep + self.translation_jar_name
        print('复制 %s 到 %s' % (self.translation_jar, jar_file_path))
        shutil.copyfile(self.translation_jar, jar_file_path)

        pre_jar_name = 'resources_cn_%s_%s_r%s.jar' % (self.name, self.pre_version, self.pre_release_version)
        pre_jar_file_path = self.path + os.sep + 'lib' + os.sep + pre_jar_name
        if os.path.exists(pre_jar_file_path):
            os.remove(pre_jar_file_path)
        else:
            print('上一版本 %s 不存在' % pre_jar_file_path)

    def validate_version(self):
        """校验是否已更新软件"""

        build_file_path = self.path + os.sep + 'build.txt'
        if not os.path.exists(build_file_path):
            print('build.txt 不存在')
            return

        pre_build_file_path = '%s/jars/%s/英文包/%s/%s' % (self.work_dir, self.name, self.pre_version, 'build.txt')
        if not os.path.exists(pre_build_file_path):
            print('上一版本的 build.txt 不存在')
            return

        print('比较 %s 和 %s' % (build_file_path, pre_build_file_path))
        if filecmp.cmp(build_file_path, pre_build_file_path):
            print('当前版本与前一版本相同，请先更新软件')
            return
        else:
            print('不相同')
            print(filex.read_lines(build_file_path))
            print(filex.read_lines(pre_build_file_path))

    def compare_jar(self):
        """比较 jar 包是否变化"""
        f1 = self.en_jar_path
        f2 = '%s/jars/%s/英文包/%s/%s' % (self.work_dir, self.name, self.pre_version, 'resources_en.jar')
        if not os.path.exists(f1):
            print('不存在 %s' % f1)
        if not os.path.exists(f2):
            print('不存在 %s' % f2)
        print('比较 %s 与 %s' % (f1, f2))
        if filecmp.cmp(f1, f2):
            print('jar 包完全相同')
            return
        print('1-收集要比较的文件夹')
        source_dir = '%s/target/%s/resources_en' % (self.work_dir, self.name)
        translation_dir_list = []
        for root, dirs, files in os.walk(source_dir):
            for dir_name in dirs:
                path = root + '/' + dir_name
                translation_dir_list.append(path.replace(source_dir, '').replace('\\', '/').lstrip('/'))
        print(translation_dir_list)

        print('2-解压出要比较的文件夹')
        tmp_dir1 = os.path.splitext(f1)[0]
        tmp_dir2 = os.path.splitext(f2)[0]
        ignore_ext = [
            '.png',
            '.gif',
            '.css',
        ]
        with zipfile.ZipFile(f1) as zipfile1:
            with zipfile.ZipFile(f2) as zipfile2:
                namelist1 = zipfile1.namelist()
                namelist2 = zipfile1.namelist()
                for name1 in namelist1:
                    ext = os.path.splitext(name1)[1]
                    if ext in ignore_ext:
                        continue
                    for translation_dir in translation_dir_list:
                        if name1.startswith(translation_dir):
                            # print('比较 %s' % name1)
                            if name1 in namelist2:
                                zipfile1.extract(name1, tmp_dir1)
                                zipfile2.extract(name1, tmp_dir2)
                            else:
                                print('f1 中有,但 f2 中没有')
        print('3-比较解压出的文件')
        for root, dirs, files in os.walk(tmp_dir1):
            for file_name in files:
                path1 = root + '/' + file_name
                path2 = path1.replace(tmp_dir1, tmp_dir2)
                if not os.path.exists(path2):
                    print('%s 不存在' % path2)
                    continue
                if not filecmp.cmp(path1, path2):
                    print('不相同 %s 与 %s' % (path1, path2))
                else:
                    # 相同,将文件删除
                    # print('文件相同 %s 与 %s' % (path1, path2))
                    os.remove(path1)
                    os.remove(path2)

    def delete_compare_tmp_dir(self):
        """删除比较时解压的临时文个夹"""
        f1 = self.en_jar_path
        f2 = '%s/jars/%s/英文包/%s/%s' % (self.work_dir, self.name, self.pre_version, 'resources_en.jar')
        tmp_dir1 = os.path.splitext(f1)[0]
        tmp_dir2 = os.path.splitext(f2)[0]
        if os.path.exists(tmp_dir1):
            print('删除 %s' % tmp_dir1)
            shutil.rmtree(tmp_dir1)
        if os.path.exists(tmp_dir2):
            print('删除 %s' % tmp_dir2)
            shutil.rmtree(tmp_dir2)

    def extract_jar_to_source_dir(self):
        """将 jar 解压到 source 目录"""
        f1 = self.en_jar_path
        print('1-收集要解压的文件夹')
        source_dir = '%s/target/%s/resources_en' % (self.work_dir, self.name)
        translation_dir_list = []
        for root, dirs, files in os.walk(source_dir):
            for dir_name in dirs:
                path = root + '/' + dir_name
                translation_dir_list.append(path.replace(source_dir, '').replace('\\', '/').lstrip('/'))
        print(translation_dir_list)

        print('2-解压出要文件夹')
        tmp_dir1 = '%s/source/%s/resources_en' % (self.work_dir, self.name)
        ignore_ext = [
            '.png',
            '.gif',
            '.css',
            '.txt',
        ]
        with zipfile.ZipFile(f1) as zipfile1:
            namelist1 = zipfile1.namelist()
            for name1 in namelist1:
                ext = os.path.splitext(name1)[1]
                if ext in ignore_ext:
                    continue
                for translation_dir in translation_dir_list:
                    if name1.startswith(translation_dir):
                        print('解压 %s 到 %s' % (name1, tmp_dir1))
                        zipfile1.extract(name1, tmp_dir1)


class ZipTools:
    @staticmethod
    def zip_jar(source_dir, target_jar):
        """压缩文件夹"""
        print('压缩 %s 到 %s' % (source_dir, target_jar))
        filex.check_and_create_dir(target_jar)
        translation_file_list = []
        for root, dirs, files in os.walk(source_dir):
            for file_name in files:
                path = root + '/' + file_name
                translation_file_list.append(path.replace(source_dir, '').replace('\\', '/').lstrip('/'))
        with zipfile.ZipFile(target_jar, 'a') as zip_file:
            for file in translation_file_list:
                # print('压缩 %s' % file)
                zip_file.write(source_dir + os.sep + file, file)


if __name__ == '__main__':
    JetBrainsTranslator().main()