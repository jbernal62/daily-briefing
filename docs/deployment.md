# Deployment

## Prerequisites

Ensure you have completed all steps in the [Getting Started](getting-started.md) guide before deploying.

## Deployment Methods

### Standard Deploy (Recommended)

```bash
make deploy
```

This runs:
1. `sam build --profile personal` — packages the Lambda function
2. `sam deploy --profile personal --region us-east-1` — deploys to AWS

**First deployment:** SAM will run in guided mode and ask for confirmation of stack name, capabilities, and changes. Accept defaults.

**Subsequent deployments:** SAM will use the saved configuration from `.aws-sam/samconfig.toml` and perform a change-set preview before applying changes.

### Guided Deploy (First Time)

```bash
sam build --profile personal
sam deploy --guided --profile personal --region us-east-1
```

Guided mode prompts for:
- Stack name: `daily-briefing`
- AWS region: `us-east-1`
- Confirm changes: `y`
- Allow SAM CLI IAM creation: `y` (SAM needs this to create the Lambda execution role)
- Disable rollback: `n`
- Save settings to `samconfig.toml`: `y`

### Build Only

```bash
make build
```

Packages the function without deploying. Useful for verifying the build succeeds before making changes.

## SAM Configuration

The `samconfig.toml` file stores deployment parameters:

```toml
version = 0.1
[default]
[default.deploy]
[default.deploy.parameters]
stack_name = "daily-briefing"
s3_bucket = "aws-sam-cli-managed-default-samclisourcebucket-..."
s3_prefix = "daily-briefing"
region = "us-east-1"
profile = "personal"
confirm_changeset = true
capabilities = "CAPABILITY_IAM"
disable_rollback = false
```

**Important:** The `s3_bucket` is auto-created by SAM on first deployment and is managed by AWS. Do not delete it.

## Deployment Outputs

After a successful deploy, SAM prints the CloudFormation outputs:

```
Outputs
-------------------------------------------------------------------------------------------------
Key                 Description
-------------------------------------------------------------------------------------------------
BriefingTopicArn     SNS topic ARN — subscribe email or SMS endpoints here
FunctionArn          Lambda function ARN
FunctionName         Lambda function name
ScheduleRule         EventBridge schedule rule name
-------------------------------------------------------------------------------------------------
```

Save the `BriefingTopicArn` for setting up SNS subscriptions.

## What Gets Deployed

| Resource | Type | Name |
|---|---|---|
| Lambda function | `AWS::Serverless::Function` | `daily-briefing` |
| SNS topic | `AWS::SNS::Topic` | `daily-briefing` |
| EventBridge rule | Implicit | `daily-briefing-schedule` |
| IAM execution role | Implicit | `daily-briefing-role-*` |
| CloudWatch log group | Implicit | `/aws/lambda/daily-briefing` |

## Redeploying After Changes

After modifying any source code or configuration:

```bash
make deploy
```

SAM uses CloudFormation change sets, so it will only update resources that changed. For code changes, only the Lambda function package is updated.

## Cleaning Up Build Artifacts

```bash
make clean
```

Removes the `.aws-sam/` directory. Does not affect anything deployed to AWS.

## Deleting the Stack

To remove all deployed resources from AWS:

```bash
aws cloudformation delete-stack \
  --stack-name daily-briefing \
  --profile personal \
  --region us-east-1
```

This deletes the Lambda function, SNS topic, EventBridge rule, and CloudWatch log group. **Secrets in Secrets Manager are NOT deleted** — delete them manually if needed:

```bash
aws secretsmanager delete-secret \
  --secret-id daily-briefing \
  --force-delete-recovery \
  --profile personal \
  --region us-east-1

aws secretsmanager delete-secret \
  --secret-id invoice-tracker/anthropic-api-key \
  --force-delete-recovery \
  --profile personal \
  --region us-east-1
```

## CI/CD Pipeline (Future)

The project includes a GitHub Actions-ready structure. To set up automated deployments:

1. Add AWS credentials to GitHub repository secrets:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`

2. Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r src/requirements.txt
      - run: pip install aws-sam-cli
      - run: make deploy
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

## Troubleshooting Deploy Issues

| Issue | Solution |
|---|---|
| `CREATE_FAILED — ResourceExistsException` | Stack already exists. Use `make deploy` instead of a new guided deploy. |
| `CAPABILITY_IAM` required | SAM needs IAM capability for the Lambda execution role. Confirm when prompted. |
| `Access Denied` on secrets | Verify the Lambda execution role has `secretsmanager:GetSecretValue` for the correct secret ARNs. |
| SAM not found | Run `brew install aws-sam-cli` to install SAM CLI. |
| Bucket already exists | SAM auto-creates an S3 bucket on first deploy. Safe to ignore. |
