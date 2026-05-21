"""Kafka producer — publishes JSON events to any topic."""
import json
import logging
from confluent_kafka import Producer
from backend.config import settings

logger = logging.getLogger(__name__)
_producer: Producer | None = None

def _get_producer() -> Producer:
    global _producer
    if _producer is None:
        _producer = Producer({"bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS})
    return _producer

def publish_event(topic: str, payload: dict) -> None:
    try:
        _get_producer().produce(
            topic,
            key=payload.get("meeting_id", ""),
            value=json.dumps(payload).encode(),
        )
        _get_producer().poll(0)
    except Exception as e:
        logger.warning("Kafka publish failed (topic=%s): %s", topic, e)
