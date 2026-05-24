import json
import uuid
import random
from datetime import datetime, timedelta
import os

# Configuration
NUM_EVENTS = 50500
OUTPUT_DIR = "output/raw"
EVENT_TYPES = ['page_view', 'product_view', 'add_to_cart', 'purchase']
PAGE_URLS = [
    "https://shop.example.com/home",
    "https://shop.example.com/shoes",
    "https://shop.example.com/electronics",
    "https://shop.example.com/checkout"
]

def generate_user_session(user_id, start_time):
    """Generates a logical sequence of events for a single user."""
    events = []
    current_time = start_time
    
    # Everyone starts with a page view
    events.append(create_event(user_id, current_time, 'page_view'))
    
    # 70% chance to view a product
    if random.random() < 0.70:
        current_time += timedelta(seconds=random.randint(10, 120))
        product_id = random.randint(1000, 9999)
        events.append(create_event(user_id, current_time, 'product_view', product_id))
        
        # 40% chance to add to cart
        if random.random() < 0.40:
            current_time += timedelta(seconds=random.randint(15, 60))
            events.append(create_event(user_id, current_time, 'add_to_cart', product_id))
            
            # 20% chance to purchase
            if random.random() < 0.20:
                current_time += timedelta(seconds=random.randint(30, 180))
                events.append(create_event(user_id, current_time, 'purchase', product_id))
                
    return events

def create_event(user_id, timestamp, event_type, product_id=None):
    return {
        "event_id": str(uuid.uuid4()),
        "user_id": user_id,
        "event_timestamp": timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "event_type": event_type,
        "page_url": random.choice(PAGE_URLS),
        "product_id": product_id
    }

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    events_generated = 0
    file_index = 1
    current_batch = []
    batch_size = 5000
    
    # Start generating from 3 days ago
    base_time = datetime.utcnow() - timedelta(days=3)

    print("Generating clickstream events...")
    
    while events_generated < NUM_EVENTS:
        user_id = random.randint(1, 10000)
        # Randomize start time within the 3-day window
        session_start = base_time + timedelta(minutes=random.randint(0, 4320)) 
        
        session_events = generate_user_session(user_id, session_start)
        current_batch.extend(session_events)
        events_generated += len(session_events)
        
        if len(current_batch) >= batch_size:
            file_path = os.path.join(OUTPUT_DIR, f"events_batch_{file_index}.json")
            with open(file_path, 'w') as f:
                for event in current_batch:
                    f.write(json.dumps(event) + '\n')
            
            print(f"Wrote {len(current_batch)} events to {file_path}")
            file_index += 1
            current_batch = []

    # Flush remaining events
    if current_batch:
        file_path = os.path.join(OUTPUT_DIR, f"events_batch_{file_index}.json")
        with open(file_path, 'w') as f:
            for event in current_batch:
                f.write(json.dumps(event) + '\n')
        print(f"Wrote {len(current_batch)} events to {file_path}")

    print(f"Total events generated: {events_generated}")

if __name__ == "__main__":
    main()