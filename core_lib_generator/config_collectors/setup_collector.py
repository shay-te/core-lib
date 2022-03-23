import enum

from core_lib.helpers.shell_utils import input_str, input_email, input_url, input_enum, input_list, input_yes_no


class LICENSE(enum.Enum):
    __order__ = 'MIT APACHE_LICENSE_2 MOZILLA_PUBLIC_LICENSE_2'
    MIT = 1
    APACHE_LICENSE_2 = 2
    MOZILLA_PUBLIC_LICENSE_2 = 3


def generate_setup_template():
    author = input_str('Enter your name')
    author_email = input_email('Enter your email id')
    description = input_str('Enter the description about this project')
    url = input_url('Enter the project\'s url')
    license_name = input_enum(LICENSE, 'Select the License', LICENSE.MIT.value)
    add_classifiers = True
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Development Status :: 4 - Beta',
        'Development Status :: 5 - Production/Stable',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Framework :: Django :: 4.0',
        'Framework :: Flask',
        'Framework :: Jupyter',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Typing :: Typed',
    ]
    user_classifiers = []
    while add_classifiers:
        user_classifiers_input = input_list(classifiers, 'Select the classifiers for your project')
        while user_classifiers_input in user_classifiers:
            user_classifiers_input = input_list(classifiers, 'Classifier already added, please select another one')
        user_classifiers.append(user_classifiers_input)
        add_classifiers = input_yes_no('Do you want to add another classifier?', True)

    return {
        'author': author,
        'author_email': author_email,
        'description': description,
        'url': url,
        'license': LICENSE(license_name).name,
        'classifiers': user_classifiers,
    }
