import os
import requests
from github import Github
import openai

class GitHubRepoSummarizer:
    def __init__(self, github_token, ai_api_key):
        self.github_client = Github(github_token)
        self.ai_client = openai.OpenAI(api_key=ai_api_key)

    def fetch_repo_contents(self, repo_url):
        """
        Fetch repository contents and structure
        """
        repo_name = repo_url.split('/')[-2] + '/' + repo_url.split('/')[-1]
        repo = self.github_client.get_repo(repo_name)

        contents = {
            'readme': self._get_readme(repo),
            'structure': self._get_repo_structure(repo),
            'key_files': self._extract_key_files(repo)
        }
        return contents

    def _get_readme(self, repo):
        try:
            readme = repo.get_readme()
            return readme.decoded_content.decode('utf-8')
        except Exception:
            return "No README found"

    def _get_repo_structure(self, repo):
        # Simplified repo structure extraction
        return [item.path for item in repo.get_contents("")]

    def _extract_key_files(self, repo, max_files=10):
        # Extract key source code files
        contents = repo.get_contents("")
        code_files = [
            content for content in contents 
            if content.type == 'file' and any(
                content.path.endswith(ext) for ext in ['.py', '.js', '.ts', '.java', '.cpp']
            )
        ]

        return [
            {
                'path': file.path,
                'content': file.decoded_content.decode('utf-8')[:500]  # First 500 chars
            } 
            for file in code_files[:max_files]
        ]

    def generate_ai_summary(self, repo_contents):
        """
        Generate summary using AI
        """
        prompt = f"""
        Analyze this GitHub repository and provide a comprehensive summary:

        README:
        {repo_contents['readme']}

        Repository Structure:
        {repo_contents['structure']}

        Key Source Files Sample:
        {repo_contents['key_files']}

        Please provide:
        1. Project purpose and main functionality
        2. Technologies and frameworks used
        3. Key features and architecture
        4. Potential use cases
        5. Brief overview of project complexity
        """

        response = self.ai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert software engineer analyzing a GitHub repository."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content

def summarize_github_repo(repo_url, github_token, ai_api_key):
    summarizer = GitHubRepoSummarizer(github_token, ai_api_key)
    repo_contents = summarizer.fetch_repo_contents(repo_url)
    summary = summarizer.generate_ai_summary(repo_contents)
    print(summary)
    return summary

GITHUB_TOKEN = 'example_token'
OPENAI_API_KEY = 'example_api_key'
summary = summarize_github_repo('https://github.com/Bibhavshah/role-based-auth', GITHUB_TOKEN, OPENAI_API_KEY)