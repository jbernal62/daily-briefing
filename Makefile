.PHONY: build deploy invoke invoke-aws logs clean

PROFILE   = personal
REGION    = us-east-1
FUNCTION  = daily-briefing

## Build Lambda package
build:
	sam build --profile $(PROFILE)

## Build + deploy to AWS
deploy: build
	sam deploy --profile $(PROFILE) --region $(REGION)

## Invoke the Lambda directly on AWS (immediate test run)
invoke-aws:
	@echo "Invoking $(FUNCTION) on AWS..."
	aws lambda invoke \
		--function-name $(FUNCTION) \
		--profile $(PROFILE) \
		--region $(REGION) \
		--payload '{}' \
		--log-type Tail \
		/tmp/briefing-response.json \
		--query 'LogResult' --output text | base64 -d
	@echo "\n--- Response ---"
	@cat /tmp/briefing-response.json

## Tail CloudWatch logs
logs:
	aws logs tail /aws/lambda/$(FUNCTION) \
		--profile $(PROFILE) \
		--region $(REGION) \
		--follow

## Enable/disable the schedule
schedule-on:
	aws events enable-rule --name daily-briefing-schedule \
		--profile $(PROFILE) --region $(REGION)

schedule-off:
	aws events disable-rule --name daily-briefing-schedule \
		--profile $(PROFILE) --region $(REGION)

clean:
	rm -rf .aws-sam/
