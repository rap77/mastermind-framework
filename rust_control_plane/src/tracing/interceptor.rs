use tonic::{Request, Status};
use tonic::service::Interceptor;
use uuid::Uuid;
use crate::tracing::metadata::TraceMetadata;

pub struct TraceInterceptor;

impl Interceptor for TraceInterceptor {
    fn call(&mut self, mut req: Request<()>) -> Result<Request<()>, Status> {
        // Inject trace_id into gRPC metadata for Python
        let trace_id = req.extensions_mut()
            .get::<TraceMetadata>()
            .map(|md| md.trace_id.to_string())
            .unwrap_or_else(|| Uuid::new_v4().to_string());

        req.metadata_mut()
            .insert("trace-id", trace_id.parse().unwrap());

        Ok(req)
    }
}
