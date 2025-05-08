import random
from locust import HttpUser, task, between


class InnoScreamUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.user_id = random.randint(1000, 9999)

    @task(3)
    def create_scream(self):
        payload = {
            'user_id': self.user_id,
            'text': f'Test scream {random.randint(1, 1000)}',
        }
        self.client.post('/screams', json=payload)

    @task(5)
    def get_scream(self):
        scream_id = random.randint(1, 100)
        self.client.get(f'/screams/{scream_id}')

    @task(2)
    def react_on_scream(self):
        scream_id = random.randint(1, 100)
        reactions = ['👍', '👎', '❤️', '😂', '😡']
        payload = {
            'scream_id': scream_id,
            'user_id': self.user_id,
            'reaction': random.choice(reactions),
        }
        self.client.post(f'/screams/{scream_id}/react', json=payload)

    @task(1)
    def get_stats(self):
        self.client.get(f'/analytics/{self.user_id}/stats')

    @task(1)
    def get_graph(self):
        periods = ['week', 'month', 'year']
        period = random.choice(periods)
        self.client.get(
            f'/analytics/{self.user_id}/graph', params={'period': period}
        )

    @task(1)
    def get_most_voted_scream(self):
        periods = ['day', 'week', 'month', 'year']
        period = random.choice(periods)
        self.client.get('/analytics/getMostVoted', params={'period': period})

    @task(1)
    def generate_meme(self):
        scream_id = random.randint(1, 100)
        self.client.post(
            '/memes/generate', params={'scream_id': scream_id}, timeout=60
        )
