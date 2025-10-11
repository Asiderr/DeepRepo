#!/usr/bin/env python3

import os

from google import genai


class DeepGenai:
    """
    Class for interacting with the Gemini API for AI-generated content.
    """
    def setup_gemini_api(self):
        if not hasattr(self, "log"):
            raise RuntimeError("Logger not initialized. "
                               "Call setup_logger() first.")
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("No GEMINI_API_KEY found"
                             "in environment variables.")
        try:
            self.gemini_client = genai.Client(api_key=api_key)
        except Exception as e:
            self.log.error(f"Failed to initialize Gemini API client: {e}")
            raise RuntimeError("Gemini API client initialization failed.")

    def generate_cluster_title(self, titles):
        if not hasattr(self, "log"):
            raise RuntimeError("Logger not initialized. "
                               "Call setup_logger() first.")

        if not hasattr(self, "gemini_client"):
            raise RuntimeError("Gemini client not initialized."
                               " Call setup_gemini_api() first.")

        prompt = (
            "You are an advanced data analyst and copywriter specializing in "
            "topic synthesis. Your task is to create one concise and "
            "representative title that best summarizes a group of "
            "related issues.\n"
            "Critical requirements:\n"
            "The output must be a single sentence or title phrase,"
            " ready to be used as a headline.\n"
            "The title should synthesize the main problem, goal,"
            " or theme present in the group of issues.\n"
            "Do not add any introduction, explanation, or extra text"
            " - return only the generated title.\n"
            "Here are the issue titles grouped into one cluster:\n"
            f"{titles}\n"
            "Now generate the cluster title:"
        )

        try:
            self.log.debug(f"Generating cluster title with prompt: {prompt}")
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            return f"- {response.text}"
        except Exception as e:
            self.log.error(f"Error generating cluster title: {e}")
            return None
