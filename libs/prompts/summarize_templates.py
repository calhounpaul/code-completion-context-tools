import os

ABBREVIATED_SCRIPT = """Here is a script that may be abbreviated or contain truncated lines. Please write a short summary of what the script appears to be doing. If you cannot determine the purpose of the script, respond with the exact string [_INDETERMINATE_] including the underscores and square brackets. The summary should be no more than five sentences:
<SCRIPT>
{script}
</SCRIPT>

Remember, the summary should be no more than five sentences. If you cannot summarize the script, respond with the string [_INDETERMINATE_] including the underscores and square brackets."""


SNIPPET_WITH_ABBREVIATED_CONTEXT = """Here is an abbreviated dependency list for the code snippet that will need to be summarized:
{dependencies}

Here is the abbreviated preceding context for the code snippet that will need to be summarized:
<PRECEDING_CONTEXT>
{preceding_context}
</PRECEDING_CONTEXT>

Here is the abbreviated following context for the code snippet that will need to be summarized:
<FOLLOWING_CONTEXT>
{following_context}
</FOLLOWING_CONTEXT>

Provide a one-paragraph summary of the following snippet from the above code. The summary should be no more than five sentences. If the purpose of the snippet cannot be determined, respond with the exact string [_INDETERMINATE_] including the underscores and square brackets.

<CODE_TO_SUMMARIZE>
{snippet}
</CODE_TO_SUMMARIZE>

Now, summarize the above script into a single paragraph. If you cannot summarize it for some reason, make sure you respond with the string [_INDETERMINATE_] including the underscores and square brackets. The summary should be no more than five sentences."""