# GFP Source Audio Reference Contract v1.0.0

Source-provided pronunciation/media is canonical provenance-bearing metadata, even when the current runtime cannot yet consume the binary directly.

A lexical Sense/Expression may carry `media_refs[]`. Each reference uses:
```json
{
  "media_type": "audio",
  "role": "source_pronunciation",
  "filename": "example.mp3",
  "language": "de-DE",
  "source_record_id": "...",
  "archive_source_id": "...",
  "status": "AVAILABLE|MISSING|UNVERIFIED",
  "sha256": null
}
```

Rules:
- preserve zero, one, or multiple audio refs in source order;
- parse every `[sound:filename]` occurrence, including concatenated multi-audio cells;
- when archive membership can be inspected, every referenced filename must be reported AVAILABLE or MISSING;
- never synthesize a filename or silently drop a second source audio file;
- shared files may be referenced by several source occurrences; this is not a duplicate error;
- binary SHA-256 is optional until bytes are individually extracted; archive membership validation is still useful evidence;
- missing source audio does not invent TTS. Runtime TTS, if available, is a separate runtime capability;
- projected vocabulary cards preserve `source_audio_refs` in `customFields` until/unless the runtime defines a stronger first-class audio ingestion field. Stage 6 must explicitly verify actual Audio-mode behavior.
