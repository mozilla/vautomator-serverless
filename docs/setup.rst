********************************
Custom Development / Deployment
********************************

.. note:: If you are simply a consumer of the service, you DO NOT have to deploy your own instance.
   Assuming you have the API key, you can use the already deployed instance at https://vautomator.security.allizom.org.

If you would like to customise and/or deploy your own instance in your AWS environment, follow the below steps:

1.  Install python3, node.js and
    `aws-cli <https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html>`__.
2.  Install serverless framework: ``npm install -g serverless``
3.  Download the repo:
    ``git clone https://github.com/mozilla/vautomator-serverless.git && cd vautomator-serverless``
4.  Create a virtual env: ``pipenv --python 3.x``
5.  Install the Python requirements: ``pip install -r requirements.txt``
6.  Customise your ``serverless.yml`` file, in particular the ``custom``
    and ``provider`` sections where you can specify your own S3 bucket
    name/SQS name/KMS key (if using Tenable.io integration, see step 6)
    etc. or specify multiple environments, tag your resources etc.
7.  Setup your AWS profile and credentials. An account or role with at least the permissions listed in
    `serverless.yml <https://github.com/mozilla/vautomator-serverless/blob/master/serverless.yml#L12-L36>`__
    is required in order to deploy and run this. If you access AWS via SSO, it is recommended to install `maws <https://pypi.org/project/mozilla-aws-cli-mozilla>`__, and use ``maws`` to sign in to assume a role. ``maws`` will obtain the session credentials for you (depending on how you used it), save these credentials in your local AWS credential file ``~/.aws/credentials``.
8.  Once your AWS profile is set up, modify the ``Makefile`` to specify
    your ``AWS region`` and ``AWS profile``. Serverless framework
    supports role assumption, and so does the ``Makefile``, as long as
    your AWS config and credentials files are setup as per
    `here <https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-role.html>`__, or using ``maws`` in the previous step.
9.  *[OPTIONAL]* If you want Tenable.io support via the
    ``/ondemand/tenablescan`` endpoint (otherwise skip to step 8):

    -  Create a Tenable.io user account with *standard* user
       permissions, and create an API key for this account.
    -  Modify the top of the ``Makefile`` as follows:

    .. code:: bash

       AWS_PROFILE := <YOUR-AWS-PROFILE/ROLE>
       # Y for Tenable.io support, N or blank if not
       TENABLE_IO := Y / N 
       
       # If you would like to create a dedicated KMS for vautomator,
       # specify a policy file here (an example policy file is
       # provided in the repository). Otherwise leave blank if
       # you would like to use default AWS SSM key for encrypted storage
       KMS_POLICY_FILE := <YOUR-KMS-POLICY-JSON-FILE>
       
       # Blank if a policy file is specified, 
       # or if you would like to use default AWS SSM key
       KMS_KEYID := <YOUR-KMS-KEY-ID> 

    -  Once this is done, run
       ``make setup TIOA=<Tenable-Access-Key> TIOS=<Tenable-Secret-Key>``.
       ``TIOA`` and ``TIOS`` are API keys generated in the first bullet point
       above. Based on the above values in Makefile, this will create a
       new or use the default AWS KMS key of your AWS account, and store the Tenable API
       keys in SSM in encrypted form using the KMS key. 
       
       .. note:: If Tenable.io integration is desired, The most straightforward option is to specify the AWS profile and ``Y`` for ``TENABLE_IO``, and leave other variables blank.
10.  *[OPTIONAL]* Run: ``make validate`` to check if your ``serverless.yml`` is correctly formatted without deploying a stack.

11. Run ``make deploy`` to deploy to AWS! This will first install the required serverless plugins, then deploy the stack.

12. If you have no serverless/CloudFormation errors and if you see
    ``Service Information`` listing your lambda functions/endpoints in the output, you are good to go.