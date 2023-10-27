---
layout: post
title:  "Jenkins - Parallel Builds"
date:   2023-10-09 14:10:00 +0530
categories: devops cicd jenkins
tags: devops cicd jenkins
---
# Introduction
When I initially began using Jenkins years ago, my initial perception of it was that it merely functioned as an advanced cron job runner, offering the unique selling point of centralized management and control over scheduled tasks from a central server. 😄 However, this perception was quickly dispelled as I delved deeper into Jenkins' vast array of plugins, robust community support, and continuous enhancements to its domain-specific language (DSL).
In this article, my aim is to shine a spotlight on Jenkins' remarkable ability to execute parallel stages within a single declarative pipeline. For those who are well-acquainted with the matrix support in GitHub Actions, I will endeavor to demonstrate a comparable level of functionality by harnessing the power of Jenkins through a combination of declarative and scripted pipelines.
![Jenkins - Parallel Builds](/assets/jenkins-parallel.png)

# Use Case - I
In this scenario, the count of parallel stages remains fixed, meaning we are aware from the outset of the exact number of parallel stages needed. For instance, our objective is to concurrently perform builds on Windows, Mac, and Linux platforms.

In this example, we will employ a single declarative pipeline, under the assumption that our Jenkins Agents, whether static or dynamically provisioned, have been preconfigured with specific labels:
- Windows Agent labeled as WIN
- Mac Agent labeled as OSX
- Ubuntu Agent labeled as LINUX

**[Jenkinsfile](https://github.com/prakritish/jenkins-parallel/blob/master/use-case-1.groovy)**
```
pipeline {
  agent any
  options {
    timestamps ()
  }
  stages {
    stage("Pre-Parallel Stage") {
      steps {
        echo "This is pre-parallel stage"
      }
    }
    stage("Parallel Tests") {
      parallel {
        stage("Windows Test") {
          agent {
            label "WIN"
          }
          steps {
            echo "Running on Windows"
          }
          post {
            always {
              echo "Job on Windows Completed"
            }
            failure {
              echo "Windows Job Failed"
            }
            success {
              echo "Windows Job Successful"
            }
          }
        }
        stage("Mac Test") {
          agent {
            label "OSX"
          }
          steps {
            echo "Running on Mac"
          }
          post {
            always {
              echo "Job on Mac Completed"
            }
            failure {
              echo "Mac Job Failed"
            }
            success {
              echo "Mac Job Successful"
            }
          }
        }
        stage("Linux Test") {
          agent {
            label "LINUX"
          }
          steps {
            echo "Running on Linux"
          }
          post {
            always {
              echo "Job on Linux Completed"
            }
            failure {
              echo "Linux Job Failed"
            }
            success {
              echo "Linux Job Successful"
            }
          }
        }
      }
    }
    stage("Post-Parallel Stage") {
      steps {
        echo "This is post-parallel stage"
      }
    }
  }
}
```
When this job is executed, this is how it shows up in BlueOcean.
![Use Case - I](/assets/parallel-use-case-1.png)

## Use Case - II

In this particular use case, we'll be employing a multidimensional matrix. Let's consider an application that necessitates building for Windows, Linux, and Mac platforms. On each of these platforms, we have to build the application using Node Versions "12.22.12," "14.21.3," "16.20.2," and "18.18.0." Consequently, the total count of required builds amounts to 3 platforms multiplied by 4 Node Versions, resulting in a total of 12 unique builds.

**[Jenkinsfile](https://github.com/prakritish/jenkins-parallel/blob/master/use-case-2.groovy)**
```
pipeline {
  // We don't care where this pipeline runs
  agent any
  options {
    timestamps ()
    skipDefaultCheckout()
  }
  stages {
    stage("Pre-Parallel Stage") {
      steps {
        echo "This is Pre-Parallel Stage"
      }
    }
    stage("Matrix Stages") {
      matrix {
        axes {
          axis {
            name "LABEL"
            values "WIN", "OSX", "LINUX"
          }
          axis {
            name "NODE_VERSION"
            values "12.22.12", "14.21.3", "16.20.2", "18.18.0"
          }
        }
        agent {
          label "${LABEL}"
        }
        stages {
          stage("Build") {
            steps {
              echo "Do Build for OS: ${LABEL} - Node Version: ${NODE_VERSION}"
            }
          }
          stage("Report") {
            steps {
              echo "Done"
            }
          }
        }
        post {
          always {
            echo "Build completed for OS: ${LABEL} - Node Version: ${NODE_VERSION}"
          }
        }
      }
    }
  }
  post {
    always {
      echo "All Done!"
    }
  }
}
```
### Explanation
The matrix section provides the capability to construct a multidimensional matrix for job execution. The stages within this section are executed concurrently. In this instance, we've established a two-dimensional matrix, with one dimension dedicated to Platform Labels and the other for Node Versions. These are represented as name-value pairs, and the name associated with each pair can be accessed as a variable within the defined stages.
```
      matrix {
        axes {
          axis {
            name "LABEL"
            values "WIN", "OSX", "LINUX"
          }
          axis {
            name "NODE_VERSION"
            values "12.22.12", "14.21.3", "16.20.2", "18.18.0"
          }
        }
        ...
        ...
      }
```  
<br />

![Use Case - II](/assets/parallel-use-case-2.png)

### Important Note:
* I want to highlight that the BlueOcean plugin I am presently utilizing may not consistently render the matrix jobs accurately. I've observed that the rendering behavior might differ from one build to another.
* It's also worth noting that I haven't discovered a method to dynamically generate the matrix axis, meaning it cannot be updated on the fly and necessitates hardcoding in the pipeline. Hopefully, in the future, we will have the option to employ Groovy Scripts to create the matrix and its axes without the need for hardcoding values.

## Use Case - III
In this scenario, the number of parallel stages is undetermined, and the identical code will be executed multiple times. For instance:
### 1. Building Code with Variations:
We are required to build the same code with different versions of Node.js and on multiple platforms, depending on user input. This means that the number of parallel stages necessary for this operation cannot be predetermined, as it relies on user specifications.
### 2. Vulnerability Scanning:
Another instance involves scanning all repositories in a GitHub Organization for vulnerabilities. Similar to the code building scenario, the number of repositories and, consequently, the number of parallel stages for vulnerability scanning is unknown in advance.

In both cases, the exact count of parallel stages required cannot be anticipated during the pipeline creation process. The objective here aligns with Use Case - II; however, in this scenario, we opt for the use of the 'parallel' directive instead of employing a matrix. Additionally, the number of parallel jobs can be dynamic, and there's no need for prior knowledge while setting up the pipeline.

**[Jenkinsfile](https://github.com/prakritish/jenkins-parallel/blob/master/use-case-3.groovy)**
```
@Library("parallel-jobs") _

// Emulating user input or input from external sources below
// Creating a string array named versions to denote the list of NodeJs versions to use
String[] versions = ["12.22.12", "14.21.3", "16.20.2", "18.18.0"]
// Creating a string array name osLabel to denote the different OS's we are going to use
String[] osLabel = ["WIN", "OSX", "LINUX"]
// The total numer of parallel jobs would versions.size() * osLabel.size()
// In this example total number of parallel jobs = 4 * 3 = 12

pipeline {
  // We don't care where this pipeline runs
  agent any
  options {
    timestamps ()
  }
  stages {
    stage("Pre-Parallel Stage") {
      steps {
        echo "This is Pre-Parallel Stage"
      }
    }
    stage("Parallel Stages") {
      steps {
        script {
          // This map 'targets' would contain a named list of jobs to be executed in parallel
          def targets = [:]
          for (String node : versions) {
            for (String os : osLabel) {
              // Populating the map 'targets'
              // nodeBuild(String, String) is coming from shared library 'vars/nodeBuild.groovy'
              targets["${os}-${node}"] = nodeBuild(node, os)
            }
          }
          // Starting the parallel jobs
          parallel targets
        }
      }
    }
  }
}
```

**Shared Library: [vars/nodeBuild.groovy](https://github.com/prakritish/jenkins-parallel/blob/master/vars/nodeBuild.groovy)**
```
def call(String nodeVersion, String label) {
    // The variable parallelStage will be used to store the code for one of the parallel job.
    // This is dynamically getting generated with the received inputs.
    def parallelStage = {
        // We specify the label of the Jenkins Agent where this particular job will be executed
        node("${label}") {
            stage("Node: ${nodeVersion}, OS: ${label}") {
                stage("Build") {
                    echo "Building on OS: ${label} with Node Version: ${nodeVersion}"
                    // Sleeping for random number of seconds to emulate a build job
                    sleep(Math.abs(new Random().nextInt() % 60) + 1)
                }
                stage("Report") {
                    echo "Build completed!"
                }
            }
        }
    }
    return parallelStage
}
```
When this job is executed, this is how it shows up in BlueOcean.
![Use Case - III](/assets/parallel-use-case-3.png)

### Important Notes:
1. **Pipeline Structure Mix:** While the primary pipeline is structured as a Declarative pipeline, the parallel stages are implemented using a Scripted pipeline. This is a current limitation when we attempt to dynamically generate parallel stages programmatically.
2. **Post-Parallel Stages Rendering:** Within the main Declarative pipeline, it is possible to have stages following the parallel execution stages. While these subsequent stages execute as expected, it's important to note that BlueOcean may not visually render them correctly at present. However, this rendering issue may be resolved in future updates of BlueOcean.
3. **Handling Issues in Scripted Pipeline:** The 'post' section, commonly used for error handling and corrective measures, is not available for Scripted pipelines. Therefore, in Scripted pipelines, you will need to employ constructs like 'try,' 'catch,' and 'finally' to effectively capture and address any encountered issues. 

Here's an example of how to use these constructs:
```
try {
    // Your scripted pipeline code here
} catch (Exception e) {
    // Handle the exception and take corrective measures
} finally {
    // This section will always be executed, regardless of whether an exception occurred or not
}
```
Please note that these limitations and workarounds are based on the current state of Jenkins and its plugins, and they may evolve with future updates and improvements.

## Use Case - IV

With the above Use Case - III, there is one notable drawback: it aims to utilize all available Jenkins Agents configured with the specified Label(s). Consequently, there is limited control over how many concurrent jobs are initiated simultaneously, potentially causing resource contention and affecting other jobs attempting to use the same set of Label(s).

To address this concern, we will introduce a variable named NO_OF_THREADS which will allow us to exert control over this behavior. By setting the NO_OF_THREADS variable, we can limit the number of concurrent jobs to a maximum of NO_OF_THREADS. This approach helps manage resource utilization and ensures that other jobs utilizing the same Label(s) are not starved of resources.

**[Jenkinsfile](https://github.com/prakritish/jenkins-parallel/blob/master/use-case-4.groovy)**
```
pipeline {
  agent any
  options {
    timestamps()
    skipDefaultCheckout()
  }
  environment {
  // Setting these as Environment variables for the example.
  // Ideally these should come as parameter from Jenkins.
    NO_OF_THREADS = 5
    AGENT_LABEL = "LINUX"
    GITHUB_REPOS = """
      https://github.com/actions/heroku.git
      https://github.com/actions/github.git
      https://github.com/actions/labeler.git
      https://github.com/actions/toolkit.git
      https://github.com/actions/runner.git
      https://github.com/actions/setup-node.git
      https://github.com/actions/runner-images.git
      https://github.com/actions/setup-go.git
      https://github.com/actions/setup-dotnet.git
      https://github.com/actions/setup-python.git
      https://github.com/actions/upload-artifact.git
      https://github.com/actions/download-artifact.git
      https://github.com/actions/typescript-action.git
      https://github.com/actions/container-action.git
      https://github.com/actions/setup-ruby.git
      https://github.com/actions/setup-java.git
      https://github.com/actions/checkout.git
      https://github.com/actions/starter-workflows.git
      https://github.com/actions/container-toolkit-action.git
      https://github.com/actions/first-interaction.git
      https://github.com/actions/hello-world-javascript-action.git
      https://github.com/actions/stale.git
      https://github.com/actions/hello-world-docker-action.git
      https://github.com/actions/example-services.git
      https://github.com/actions/setup-elixir.git
      https://github.com/actions/github-script.git
      https://github.com/actions/javascript-action.git
      https://github.com/actions/create-release.git
      https://github.com/actions/upload-release-asset.git
      https://github.com/actions/setup-haskell.git
    """
  }
  stages {
    stage("Pre Parallel") {
      steps {
        echo "This is Pre Parallel Stage"
      }
    }
    stage("Parallel Stage") {
      steps {
        script {
          // We'll use this Array to store all the repositories provided.
          def repos = []
          // Removing any white spaces and splitting it
          def repoList = env.GITHUB_REPOS.strip().split('\n')
          for (String repo: repoList) {
            if (repo) {
              // Strip white spaces and add it to the Array.
              repos.add(repo.strip())
            }
          }
          def repoCount = repos.size()
          def threads = env.NO_OF_THREADS.toInteger()
          echo "No. of Parallel Scans allowed: ${NO_OF_THREADS}"
/*
          This is important to note. The `repos` is a single dimensional array
          We are using 'collate' to convert this into a two dimensinal array.
          Say,
            repos = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k"]
          The statement
            repo_group = repos.collate 4
          would create a two dimensional array as
            repo_group = [
              ["a", "b", "c", "d"], 
              ["e", "f", "g", "h"],
              ["i", "j", "k"]
            ]
          Or in other words, split the original array into an array of smaller arrays.
*/
          def repo_group = repos.collate threads
          for (def row : repo_group) {
            def targets = [:]
            for (String repo : row) {
              // We pass the empty map targets by reference to generateTargets along with other
              // parameters. The function generateTargets populates the map 'targets'
              generateTargets(targets, repo, env.AGENT_LABEL)
            }
            // Execute parallel stages
            parallel targets
          }
        }
      }
    }
  }
}

def generateTargets(def targets, String repo, String label) {
  targets[repo] = {
    node(label) {
      stage('Scan') {
        try {
          echo "Use this stage to scan ${repo}"
        } catch (err) {
            echo err.toString()
            unstable("endorctl Scan failed for ${project}")
        }
      }
    }
  }
}
```
When this job is executed, this is how it shows up in BlueOcean.
![Use Case - IV](/assets/parallel-use-case-4.png)

### Important Note:
* While utilizing the approach of grouping jobs into batches and controlling the number of concurrent stages with the NO_OF_THREADS variable, it's essential to be mindful of another potential downside. Specifically, it's advisable to strive for a balance where each parallel stage within a group requires a similar amount of time to complete.
* In this grouping strategy, Jenkins follows a sequential execution pattern, waiting for all parallel stages within a group to finish before moving on to the next group. This means that if the first group contains a job that takes an hour to complete, while the other jobs in the group finish in just 5 minutes, Jenkins will patiently wait for the full one hour, holding up the processing of the next batch of jobs. Therefore, it's crucial to aim for relative parity in execution times to optimize pipeline efficiency.

### Reference:
I have uploaded all the pipelines and shared library used in the above examples at [https://github.com/prakritish/jenkins-parallel.git](https://github.com/prakritish/jenkins-parallel.git)
