---
layout: post
title:  "Jenkins - Shared Library"
date:   2023-10-05 14:10:00 +0530
categories: devops cicd jenkins
tags: devops cicd jenkins
---
![Jenkins Shared Library](/assets/jenkins-shared-library.png)
# Introduction
A Jenkins Shared Library is a powerful feature that allows you to share and reuse code across multiple Jenkins pipelines or jobs. It is essentially a collection of reusable Groovy scripts and resources that can be accessed and utilized in various Jenkinsfile scripts. This feature streamlines your Jenkins automation and promotes code reusability, maintainability, and consistency across your projects.

# Key Components
```
my-shared-library/
├── src/
│   ├── utils/
│   │   └── commonUtils.groovy
│   ├── api/
│   │   ├── apiClient.groovy
│   │   └── apiUtils.groovy
│   └── ...
├── vars/
│   ├── myFunction.groovy
│   └── ...
├── resources/
│   ├── config.json
│   └── ...
└── README.md
```
## 1. Resources
The "Resources" directory is especially relevant when you are working with an external Shared Library, as it enables the use of the libraryResource step to access files within that directory.
This feature allows you to separate non-Groovy resources from your Groovy scripts, making it easier to manage and access these files when needed.
## 2. Vars Directory
The vars directory is a special directory within your Shared Library where you define global variables or functions that can be directly called in your Jenkinsfiles without the need to import or reference the library explicitly.
## 3. src Directory
While not mandatory, you can organize your Groovy scripts within the src directory for better structure and separation of concerns.
# Benefits
1. **Reusability**: Shared Libraries allow you to write code once and use it across multiple Jenkins pipelines, reducing duplication and ensuring consistency.
2. **Maintainability**: Centralizing your common scripts and resources in a Shared Library makes it easier to manage and update them as needed.
3. **Customization**: You can tailor the Shared Library to your organization's specific needs, incorporating best practices, security checks, and more.
4. **Version Control**: Shared Libraries can be versioned using Git or other version control systems, ensuring that you can track changes and roll back if necessary.
# Usage
1. **Library Configuration**: To use a Shared Library in Jenkins, you need to configure it in the Jenkins Global Configuration settings. You specify the library's name, source code repository, and version.
2. **Importing in Jenkinsfiles**: In your Jenkinsfile scripts, you import the Shared Library using the @Library annotation. This makes the library's functions and variables available for use.
3. **Accessing Global Variables**: Global variables defined in the vars directory can be used directly in your Jenkinsfiles without importing the library explicitly.

# How to use Jenkins Shared Library
## Configure Jenkins
1. Login to your Jenkins with administrative privilege.
2. Go to _Manage Jenkins --> System (in System Configuration block)_
3. Search for *Global Pipeline Libraries*, and click *Add* button.
4. Give it a *Name*, e.g., _shared-lib_
5. Specify the default version to use. This might be a branch name, tag, commit hash, etc., according to the SCM. For our example, we will set it to main branch.
6. For Retrieval method choose the relevant settings.

![Global Shared Library Setting](/assets/global-shared-library.png)

## Shared Library
For our example, we will create two different library files.
The first one uses the /vars directory and accesses the functions without explicit import. Please see the inline comments for better understanding.

**Filename:** `vars/utils.groovy`
```
/*
Default function for the Groovy file. Use this function as below
from your pipeline i.e., use the file's basename as a function
while calling it from your script.

    script {
        utils()
    }

*/
def call() {
    echo "This is the default function of the shared library 'Util.groovy'"
}

/*
This function should be called as below:

    script {
        utils.ping("google.com")
    }

i.e., the function should be prefixed with the file's basename.
*/

def ping(String host) {
    def cmd = "ping -c 3 " + host
    sh cmd
}
```
The second one uses the /src directory with a much more structured/organised way of creating a Shared Library. Please see the inline comments for better understanding.

**Filename:** `src/com/seneshore/Hello.groovy`
```
package com.seneshore
/*
See the package name structure. This file is under
    /src/com/seneshore
and the package is named 'com.seneshore'
*/

/*
The class name and file's basename should be the same.
Here the file name is Hello.groovy, so we are using the
class name as 'Hello'.
*/
class Hello implements Serializable {
    def call(def pipeline, String name) {
        return exec(pipeline, name)
    }

    def exec(def pipeline, String name) {
        pipeline.echo "Hello ${name}!"
    }
}
```
Now the main declarative pipeline script Jenkinsfile

**Filename:** `Jenkinsfile`
```
/*
The line below defines the library path. The above refers to the settings
created on the Jenkins.
Optionally you may also pin it to specific version like
    @Library("shared-lib@v1.0.0") _
The _ (underscore) at the end denotes that we would like to import
all the Globals under `var` directory.
*/
@Library("shared-lib") _

// Import the library
import com.seneshore.Hello

// Create an object of the Class Hello
def Hello = new Hello()

pipeline {
    agent any
    options {
        timestamps ()
    }
    stages {
        stage("utill Default") {
            steps {
                script {
                    utils()
                }
            }
        }
        stage("util ping") {
            steps {
                script {
                    utils.ping("google.com")
                }
            }
        }
        stage("Hello") {
            steps {
                script {
                    // This uses the default method 'call' of the Class Hello
                    Hello(this, "Prakritish")
                    // Explicitly calling Public method `exec` of the Class Hello
                    Hello.exec(this, "Mr. Sen Eshore")
                }
            }
        }
    }
}
```

My directory structure looks like this:
```
tree
.
├── Jenkinsfile
├── README.md
├── src
│   └── com
│       └── seneshore
│           └── Hello.groovy
└── vars
    └── utils.groovy

5 directories, 4 files
```
Now the only thing left is to create a new job in Jenkins and use it.

![Blue Ocean](/assets/blue-ocean-shared-library.png)

## Console Log:
![Console Log](/assets/console-log.png)

# Reference
* [https://github.com/prakritish/jenkins-shared-library](https://github.com/prakritish/jenkins-shared-library)
