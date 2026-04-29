use tonic::{Request, Status};
use tonic::service::Interceptor;
use uuid::Uuid;
use crate::tracing::metadata::TraceMetadata;

/// gRPC client interceptor that propagates `trace_id` in outgoing metadata.
///
/// The interceptor reads `TraceMetadata` from the request extensions (set by
/// the Axum [`super::middleware::inject_trace_middleware`]) and injects the
/// `trace-id` gRPC metadata key so the Python service can extract it.
///
/// If no metadata is found in extensions (e.g., a gRPC call made outside an
/// HTTP request context), a fresh UUID v4 is generated.
pub struct TraceInterceptor;

impl Interceptor for TraceInterceptor {
    fn call(&mut self, mut req: Request<()>) -> Result<Request<()>, Status> {
        // Read trace_id from extensions (set by HTTP trace middleware)
        let trace_id = req
            .extensions()
            .get::<TraceMetadata>()
            .map(|md| md.trace_id.clone())
            .unwrap_or_else(|| Uuid::new_v4().to_string());

        req.metadata_mut()
            .insert("trace-id", trace_id.parse().map_err(|_| {
                Status::internal("invalid trace_id for gRPC metadata")
            })?);

        Ok(req)
    }
}
