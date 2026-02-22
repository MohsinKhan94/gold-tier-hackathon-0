# Create Tweet



<EndpointHeader method="POST" path="/twitter/tweet/create" />

This endpoint costs `$0.001` per API call.

Request Body [#request-body]

| Field               | Type             | Required | Description                                                |
| ------------------- | ---------------- | -------- | ---------------------------------------------------------- |
| `auth_token`        | string           | Yes      | User's auth token                                          |
| `text`              | string           | Yes      | Tweet text                                                 |
| `reply_to_tweet_id` | string           | No       | Tweet id to reply to                                       |
| `media_ids`         | array of strings | No       | Pre-uploaded Twitter media ids                             |
| `media_urls`        | array of strings | No       | URLs to images/videos — fetched and uploaded automatically |
| `media`             | array of objects | No       | Base64-encoded media — uploaded automatically              |
| `media[].data`      | string           | Yes\*    | Base64-encoded file content                                |
| `media[].type`      | string           | Yes\*    | MIME type (e.g. `image/png`, `video/mp4`)                  |

\* Required when using the `media` field.

Notes [#notes]

* Creates a tweet for the auth token owner.
* Supports 3 ways to attach media (can be mixed in a single request):
  * `media_ids` — use if you already have Twitter media ids
  * `media_urls` — pass image/video URLs, the server fetches and uploads them to Twitter
  * `media` — pass base64-encoded files inline
* For videos, the server handles chunked upload (INIT → APPEND → FINALIZE) and waits for processing to complete.
* If X rejects the mutation, this endpoint returns `502`.

Media Limits [#media-limits]

Images (all tiers) [#images-all-tiers]

|                  | Limit                        |
| ---------------- | ---------------------------- |
| Max per tweet    | 4 images                     |
| File size        | 5 MB (JPEG/PNG), 15 MB (GIF) |
| Formats          | JPEG, PNG, GIF, WEBP         |
| Recommended size | 1600 × 900 px (16:9)         |

GIFs (all tiers) [#gifs-all-tiers]

|               | Limit                      |
| ------------- | -------------------------- |
| Max per tweet | 1 GIF                      |
| File size     | 15 MB (mobile), 5 MB (web) |

Videos [#videos]

|               | Free         | Premium                  | Premium+          |
| ------------- | ------------ | ------------------------ | ----------------- |
| Max duration  | 2 min 20 sec | \~3 hours                | 4 hours (web/iOS) |
| File size     | 512 MB       | 8 GB                     | 16 GB             |
| Android max   | 2:20         | 10 min                   | 10 min            |
| Resolution    | 1080p        | 1080p (≤2h), 720p (2–4h) | Same as Premium   |
| Formats       | MP4, MOV     | MP4, MOV                 | MP4, MOV          |
| Max per tweet | 1 video      | 1 video                  | 1 video           |

<Callout type="info">
  Limits depend on the X account tier of the `auth_token` owner. Most accounts are free tier (2 min 20 sec video, 512 MB max).
</Callout>

Response (200) [#response-200]

```json
{
  "status": "success",
  "msg": "Tweet created successfully",
  "data": {
    "id": "2019384131067818211",
    "text": "Hello world!",
    "createdAt": "Thu Feb 05 12:14:29 +0000 2026"
  }
}
```

Error Responses [#error-responses]

400 - Missing fields [#400---missing-fields]

```json
{
  "error": "Missing required field: text"
}
```

401 - Invalid auth_token [#401---invalid-auth_token]

```json
{
  "error": "Invalid auth_token - could not extract userId"
}
```

502 - Mutation rejected by X [#502---mutation-rejected-by-x]

```json
{
  "error": "Tweet creation failed - Twitter did not return a tweet ID"
}
```

Examples [#examples]

Text only [#text-only]

<Tabs items={["curl", "JavaScript", "Python"]}>
  <Tab value="curl">
    ```bash
    curl -X POST "https://api.getxapi.com/twitter/tweet/create" \
      -H "Authorization: Bearer API_KEY" \
      -H "Content-Type: application/json" \
      -d '{
        "auth_token": "your_auth_token",
        "text": "Hello world!"
      }'
    ```
  </Tab>

  <Tab value="JavaScript">
    ```javascript
    const response = await fetch("https://api.getxapi.com/twitter/tweet/create", {
      method: "POST",
      headers: {
        Authorization: "Bearer API_KEY",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        auth_token: "your_auth_token",
        text: "Hello world!",
      }),
    });
    const data = await response.json();
    console.log(data);
    ```
  </Tab>

  <Tab value="Python">
    ```python
    import requests

    response = requests.post(
        "https://api.getxapi.com/twitter/tweet/create",
        headers={"Authorization": "Bearer API_KEY"},
        json={
            "auth_token": "your_auth_token",
            "text": "Hello world!",
        },
    )
    print(response.json())
    ```
  </Tab>
</Tabs>

With media URL [#with-media-url]

```bash
curl -X POST "https://api.getxapi.com/twitter/tweet/create" \
  -H "Authorization: Bearer API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "auth_token": "your_auth_token",
    "text": "Check this out",
    "media_urls": ["https://example.com/photo.jpg"]
  }'
```

With base64 media [#with-base64-media]

```bash
curl -X POST "https://api.getxapi.com/twitter/tweet/create" \
  -H "Authorization: Bearer API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "auth_token": "your_auth_token",
    "text": "Photo upload",
    "media": [{"data": "iVBORw0KGgo...", "type": "image/png"}]
  }'
```

Reply with media [#reply-with-media]

```bash
curl -X POST "https://api.getxapi.com/twitter/tweet/create" \
  -H "Authorization: Bearer API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "auth_token": "your_auth_token",
    "text": "Great thread!",
    "reply_to_tweet_id": "2019264360682778716",
    "media_urls": ["https://example.com/reaction.mp4"]
  }'
```
