"""
Kafka consumers — one per topic, run as background threads.
Each consumer processes events and triggers downstream pipelines.
"""
import json
import logging
import threading
from confluent_kafka import Consumer, KafkaError
from backend.config import settings

logger = logging.getLogger(__name__)

def _make_consumer(group_id: str, topics: list[str]) -> Consumer:
    c = Consumer({
        "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
        "group.id": group_id,
        "auto.offset.reset": "latest",
        "enable.auto.commit": True,
    })
    c.subscribe(topics)
    return c

def _consume_loop(consumer: Consumer, handler, stop_event: threading.Event):
    while not stop_event.is_set():
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() not in (KafkaError._PARTITION_EOF, KafkaError.UNKNOWN_TOPIC_OR_PART):
                logger.error("Kafka error: %s", msg.error())
            continue
        try:
            payload = json.loads(msg.value().decode())
            handler(payload)
        except Exception as e:
            logger.error("Consumer handler error: %s", e)
    consumer.close()

# ── Handlers ──────────────────────────────────────────────────────────────────

def on_transcript(payload: dict):
    """Triggered for every new transcript chunk."""
    logger.info("[transcript] meeting=%s speaker=%s text=%s",
                payload.get("meeting_id"), payload.get("speaker"), payload.get("text", "")[:60])
    # Downstream: ML pipeline + embedding are triggered via REST after meeting ends.
    # For real-time sentiment we import inline to avoid circular deps.
    try:
        from backend.ml.sentiment import score_text
        score = score_text(payload.get("text", ""))
        logger.info("[transcript] sentiment=%.3f", score)
    except Exception:
        pass

def on_speaker(payload: dict):
    logger.info("[speaker] %s", payload)

def on_summary(payload: dict):
    logger.info("[summary] meeting=%s", payload.get("meeting_id"))

def on_action_item(payload: dict):
    logger.info("[action_item] %s", payload.get("task"))

def on_alert(payload: dict):
    logger.warning("[alert] %s", payload)

# ── Start / Stop ───────────────────────────────────────────────────────────────

_stop_events: list[threading.Event] = []

def start_all_consumers():
    configs = [
        ("transcript-group", [settings.KAFKA_TOPIC_TRANSCRIPTS], on_transcript),
        ("speaker-group",    [settings.KAFKA_TOPIC_SPEAKERS],    on_speaker),
        ("summary-group",    [settings.KAFKA_TOPIC_SUMMARIES],   on_summary),
        ("action-group",     [settings.KAFKA_TOPIC_ACTION_ITEMS],on_action_item),
        ("alert-group",      [settings.KAFKA_TOPIC_ALERTS],      on_alert),
    ]
    for group_id, topics, handler in configs:
        stop = threading.Event()
        _stop_events.append(stop)
        consumer = _make_consumer(group_id, topics)
        t = threading.Thread(target=_consume_loop, args=(consumer, handler, stop), daemon=True)
        t.start()
        logger.info("Started consumer: %s → %s", group_id, topics)

def stop_all_consumers():
    for e in _stop_events:
        e.set()
