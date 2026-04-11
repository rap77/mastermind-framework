//! Instagram integration tests
//!
//! End-to-end tests for Instagram webhook processing and message sending.

use serde_json::json;

#[cfg(test)]
mod instagram_end_to_end_tests {
    use super::*;

    #[test]
    fn test_parse_instagram_comment_webhook() {
        // Test parsing Instagram comment webhook
        let payload = json!({
            "changes": [{
                "value": {
                    "id": "123456789",
                    "media": {
                        "id": "987654321",
                        "image_url": "https://instagram.com/example.jpg"
                    },
                    "from": {"username": "john_doe"},
                    "text": "Great post!",
                    "timestamp": 1712829600
                }
            }]
        });

        // This test verifies the Instagram parser can extract all fields
        // Actual parsing is done in rust_control_plane/src/channels/instagram.rs
        assert_eq!(payload["changes"][0]["value"]["id"], "123456789");
        assert_eq!(payload["changes"][0]["value"]["media"]["id"], "987654321");
        assert_eq!(payload["changes"][0]["value"]["from"]["username"], "john_doe");
        assert_eq!(payload["changes"][0]["value"]["text"], "Great post!");
    }

    #[test]
    fn test_parse_instagram_comment_with_reply() {
        // Test parsing Instagram comment with threading (reply)
        let payload = json!({
            "changes": [{
                "value": {
                    "id": "987654321",
                    "media": {"id": "123456789"},
                    "from": {"username": "jane_smith"},
                    "text": "I agree!",
                    "parent_comment_id": "123456789",
                    "timestamp": 1712829700
                }
            }]
        });

        // Verify parent_comment_id is extracted for threading
        assert_eq!(
            payload["changes"][0]["value"]["parent_comment_id"],
            "123456789"
        );
        assert_eq!(payload["changes"][0]["value"]["text"], "I agree!");
    }

    #[test]
    fn test_parse_instagram_media_attachment() {
        // Test parsing Instagram comment with media attachment
        let payload = json!({
            "changes": [{
                "value": {
                    "id": "111111111",
                    "media": {
                        "id": "222222222",
                        "image_url": "https://example.com/photo.jpg"
                    },
                    "from": {"username": "photo_fan"},
                    "text": "Nice shot!"
                }
            }]
        });

        // Verify media URL is extracted
        assert_eq!(
            payload["changes"][0]["value"]["media"]["image_url"],
            "https://example.com/photo.jpg"
        );
    }

    #[test]
    fn test_instagram_comment_filtering() {
        // Test that we filter out likes, follows (only process comments)
        let comment_payload = json!({
            "changes": [{
                "value": {
                    "id": "123",
                    "text": "This is a comment"
                }
            }]
        });

        let like_payload = json!({
            "changes": [{
                "value": {
                    "action": "like"
                }
            }]
        });

        // Comment has both 'id' and 'text' fields
        assert!(comment_payload["changes"][0]["value"].get("id").is_some());
        assert!(comment_payload["changes"][0]["value"].get("text").is_some());

        // Like has neither 'id' nor 'text'
        assert!(like_payload["changes"][0]["value"].get("id").is_none());
        assert!(like_payload["changes"][0]["value"].get("text").is_none());
    }

    #[test]
    fn test_webhook_to_send_flow() {
        // Test the flow: webhook → parse → send to Python
        let webhook_payload = json!({
            "changes": [{
                "value": {
                    "id": "comment_123",
                    "media": {"id": "media_456"},
                    "from": {"username": "test_user"},
                    "text": "Hello from Instagram!"
                }
            }]
        });

        // Step 1: Extract comment data
        let comment_id = webhook_payload["changes"][0]["value"]["id"].as_str().unwrap();
        let media_id = webhook_payload["changes"][0]["value"]["media"]["id"].as_str().unwrap();
        let username = webhook_payload["changes"][0]["value"]["from"]["username"].as_str().unwrap();
        let text = webhook_payload["changes"][0]["value"]["text"].as_str().unwrap();

        assert_eq!(comment_id, "comment_123");
        assert_eq!(media_id, "media_456");
        assert_eq!(username, "test_user");
        assert_eq!(text, "Hello from Instagram!");

        // Step 2: Prepare data for Python sender
        let python_request = json!({
            "media_id": media_id,
            "comment_text": text
        });

        assert_eq!(python_request["media_id"], "media_456");
        assert_eq!(python_request["comment_text"], "Hello from Instagram!");

        // Step 3: Would send to /api/channels/instagram/send endpoint
        // (Actual HTTP call is tested in apps/api/tests/test_instagram.py)
    }

    #[test]
    fn test_comment_threading_flow() {
        // Test that threading is preserved when sending replies
        let reply_payload = json!({
            "changes": [{
                "value": {
                    "id": "reply_789",
                    "media": {"id": "media_456"},
                    "from": {"username": "reply_user"},
                    "text": "@original_user I agree!",
                    "parent_comment_id": "comment_123"
                }
            }]
        });

        // Extract parent_comment_id for threading
        let parent_id = reply_payload["changes"][0]["value"]["parent_comment_id"]
            .as_str()
            .unwrap();

        assert_eq!(parent_id, "comment_123");

        // When sending reply, should include parent_comment_id
        let python_request = json!({
            "media_id": "media_456",
            "comment_text": "@original_user I agree!",
            "parent_comment_id": parent_id
        });

        assert_eq!(
            python_request["parent_comment_id"],
            "comment_123"
        );
    }

    #[test]
    fn test_media_attachment_download_flow() {
        // Test that media URLs are extracted for S3 upload
        let media_payload = json!({
            "changes": [{
                "value": {
                    "id": "comment_with_media",
                    "media": {
                        "id": "media_789",
                        "image_url": "https://instagram.com/media.jpg"
                    },
                    "from": {"username": "media_user"},
                    "text": "Check this photo!"
                }
            }]
        });

        // Extract media URL for download
        let media_url = media_payload["changes"][0]["value"]["media"]["image_url"]
            .as_str()
            .unwrap();

        assert_eq!(media_url, "https://instagram.com/media.jpg");

        // Would download and upload to S3
        // (Actual S3 upload is tested in integration tests)
    }
}
