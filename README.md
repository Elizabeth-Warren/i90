# I90

I90 is a link shortener. It exposes a minimal API that users can call to create new redirects. Whenever someone visits the `short_url` returned by the API, the user will be redirected to the destination the caller passed in. Records of every visit to one of these URLs are synced to Redshift/Civis within 5 minutes. Handily, API callers are encouraged to pass in additional information about the redirect they're creating. That information is carried to Redshift as well.

Data in Redshift is stored as JSON in a single column called `__raw`. This JSON is projected into a view for easy querying. Our Redshift cluster is currently disk-bound rather than CPU-bound. Using the cores available there to parse the JSON is preferable to using the disks for additional columns.

## Installation

    pipenv install -d
    npm install -g serverless@1.51.0
    npm install

## Deploy

And example `serverless.yml` is provided here. The production configuration was somewhat more complicated but not particularly so.

If a domain does not yet exist for your application stage

    sls create_domain --stage <your stage>

To deploy the code

    sls deploy --stage <your stage>

## API

Authentication to the API is mediated using API keys on the API Gateway fronting this application. You can find API keys by visiting [this page](https://console.aws.amazon.com/apigateway/home?region=us-east-1#/api-keys) and finding one associated with `i90`. You can also create a new API key on that page. YOu will need to associate that key with the `i90` API with which you'll communicate. If you have any questions about this process, please reach out to @pjstein on slack.

These API keys are passed to `i90` as the `x-api-key` header.

### GET: `v1/redirect/{token}`

Redirects are identified by a token. Pass a token to this endpoint to see what the database know about redirect identified by that token.

    # Sample Response
    {
        "updated_at": "2020-02-06T04:49:13.196004",
        "_app_name": "i90-tools",
        "destination": "https://pjstein.co",
        "dimensions_domain": "pjstein.co",
        "dimensions_scheme": "https",
        "token": "it-me"
    }

### POST: `v1/claim`

Post JSON to this endpoint with both `token` and `destination` keys in the body. The given `token` will identify the redirect, and the returned `short_url` will redirect to the given `destination`. You are encouraged to pass other descriptive information to this API as well to improve tracking on the other end. Please see the notes about "I90 Common Schema" below.

    # Sample Response
    {
        "_app_name": "i90-tools",
        "dimensions_scheme": "https",
        "dimensions_domain": "pjstein.co",
        "token": "it-me",
        "destination": "https://pjstein.co",
        "updated_at": "2020-02-06T04:49:13.196004",
        "short_url": "https://dev-i90.example.com/x/it-me"
    }

### POST: `v1/conceive`

Post JSON to this endpoint with a `destination` key in the body. I90 will generate a random token to associate with this destination.

    # Sample Response
    {
        "_app_name": "i90-tools",
        "dimensions_scheme": "https",
        "dimensions_domain": "pjstein.co",
        "token": "zp0VeK6atIobDtC-4G_Sjw",
        "destination": "https://pjstein.co",
        "updated_at": "2020-02-06T04:48:05.628244",
        "short_url": "https://dev-i90.example.com/x/zp0VeK6atIobDtC-4G_Sjw"
    }

## CLI

I90 has a small cli that exercises the API itself, rather than interacting with the database directly. This is handy for exercising the API after deploys and making new redirects on the fly.

    ➜  i90 git:(pjstein/i90-v1) ✗ pipenv run i90-tools get --api-endpoint https://dev-i90.example.com --token it-me | python -m json.tool
    [2020-02-05 23:49:50,677] [botocore.credentials] [INFO] [load] [line: 1059] - Found credentials in environment variables.
    {
        "updated_at": "2020-02-06T04:49:13.196004",
        "_app_name": "i90-tools",
        "destination": "https://pjstein.co",
        "dimensions_domain": "pjstein.co",
        "dimensions_scheme": "https",
        "token": "it-me"
    }

    ➜  i90 git:(pjstein/i90-v1) ✗ pipenv run i90-tools claim --api-endpoint https://dev-i90.example.com --token it-me --destination https://pjstein.co
    [2020-02-05 23:49:11,647] [botocore.credentials] [INFO] [load] [line: 1059] - Found credentials in environment variables.
    {
        "_app_name": "i90-tools",
        "dimensions_scheme": "https",
        "dimensions_domain": "pjstein.co",
        "token": "it-me",
        "destination": "https://pjstein.co",
        "updated_at": "2020-02-06T04:49:13.196004",
        "short_url": "https://dev-i90.example.com/x/it-me"
    }

    ➜  i90 git:(pjstein/i90-v1) ✗ pipenv run i90-tools conceive --api-endpoint https://dev-i90.example.com --destination https://pjstein.co | python -m json.tool
    [2020-02-05 23:48:05,056] [botocore.credentials] [INFO] [load] [line: 1059] - Found credentials in environment variables.
    {
        "_app_name": "i90-tools",
        "dimensions_scheme": "https",
        "dimensions_domain": "pjstein.co",
        "token": "zp0VeK6atIobDtC-4G_Sjw",
        "destination": "https://pjstein.co",
        "updated_at": "2020-02-06T04:48:05.628244",
        "short_url": "https://dev-i90.example.com/x/zp0VeK6atIobDtC-4G_Sjw"
    }

## I90 Common Schema

As an API user, you're encouraged to pass any information that could be useful in tracking the usage or performance of your redirect to I90 when you create it. While you can pass arbitrary string fields in the body of your request to the API, we recommend using a few in particular.

- `_app_name`
- `_redirect_role`
- `_identity_email`
- `_identity_phone_number`
- `_identity_zip5`
- `_identity_zip9`
- `_identity_state_code`
- `_identity_state`
- `_identity_myc_van_id`
- `_identity_heap_id`
- `_identity_bailey_id`

Using these fields makes it easier for us to develop reporting on top of our tracking data. If you cannot include these fields, no worries. But if you do have any of this information available when you're creating a redirect, it'd behoove you to include it.

## More notes about tracking

In addition to the fields you pass to I90, it parses the destination you pass as a destination and includes those parsed fields in the records it passes to Redshift. For example, a url's `utm_source` winds up as `redirect_dimensions_query_utm_source` in the tracking table.
