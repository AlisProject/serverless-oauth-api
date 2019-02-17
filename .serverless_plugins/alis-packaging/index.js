'use strict';
const BbPromise = require('bluebird')
const path = require('path')

class AlisPackaging {
  constructor(serverless, options) {
    this.serverless = serverless
    this.options = options || {}
    this.provider = this.serverless.getProvider('aws')
    this.service = this.serverless.service.service
    this.region = this.provider.getRegion()
    this.stage = this.provider.getStage()

    this.commands = {
      package: {
        options: {
          's3-bucket': {
            usage: ''
          },
          's3-key': {
            usage: ''
          },
        },
      },
    };

    this.hooks = {
      'before:package:initialize': async () => {
        if (this.options['s3-bucket']) {
          this.serverless.service.provider.deploymentBucket = this.options['s3-bucket']
        }
      },
      'after:package:compileFunctions': async () => {
        if (!this.options['s3-key']) {
          return BbPromise.resolve()
        }
        const allFunctions = this.serverless.service.getAllFunctions();
        return BbPromise.each(
          allFunctions,
          functionName => this.compileFunction(functionName)
        )
      },
    }
  }

  async compileFunction(functionName) {
    Object.keys(this.serverless.service.provider.compiledCloudFormationTemplate.Resources).forEach(resource => {
      if (this.serverless.service.provider.compiledCloudFormationTemplate.Resources[resource].Type === 'AWS::Lambda::Function') {
        const functionObject = this.serverless.service.getFunction(functionName);
        functionObject.package = functionObject.package || {};
        const serviceArtifactFileName = this.provider.naming.getServiceArtifactName();
        const functionArtifactFileName = this.provider.naming.getFunctionArtifactName(functionName);

        let artifactFilePath = functionObject.package.artifact ||
          this.serverless.service.package.artifact;
        if (!artifactFilePath ||
          (this.serverless.service.artifact && !functionObject.package.artifact)) {
          let artifactFileName = serviceArtifactFileName;
          if (this.serverless.service.package.individually || functionObject.package.individually) {
            artifactFileName = functionArtifactFileName;
          }

          artifactFilePath = path.join(this.serverless.config.servicePath
            , '.serverless', artifactFileName);
        }

        const s3FileName = artifactFilePath.split(path.sep).pop();
        this.serverless.service.provider.compiledCloudFormationTemplate.Resources[resource].Properties.Code.S3Key = this.options['s3-key'] + '/' + s3FileName
      }
    });
  }
}
module.exports = AlisPackaging;
