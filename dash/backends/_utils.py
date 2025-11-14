import traceback
import re


def format_traceback_html(error, error_handling_mode, title, backend):
    tb = error.__traceback__
    errors = traceback.format_exception(type(error), error, tb)
    pass_errs = []
    callback_handled = False
    for err in errors:
        if error_handling_mode == "prune":
            if not callback_handled:
                if "callback invoked" in str(err) and "_callback.py" in str(err):
                    callback_handled = True
                continue
        pass_errs.append(err)
    formatted_tb = "".join(pass_errs)
    error_type = type(error).__name__
    error_msg = str(error)
    # Parse traceback lines to group by file
    file_cards = []
    pattern = re.compile(r'  File "(.+)", line (\d+), in (\w+)')
    lines = formatted_tb.split("\n")
    current_file = None
    card_lines = []
    for line in lines[:-1]:  # Skip the last line (error message)
        match = pattern.match(line)
        if match:
            if current_file and card_lines:
                file_cards.append((current_file, card_lines))
            current_file = (
                f"{match.group(1)} (line {match.group(2)}, in {match.group(3)})"
            )
            card_lines = [line]
        elif current_file:
            card_lines.append(line)
    if current_file and card_lines:
        file_cards.append((current_file, card_lines))
    cards_html = ""
    for filename, card in file_cards:
        cards_html += (
            f"""
        <div class=\"error-card\">
            <div class=\"error-card-header\">{filename}</div>
            <pre class=\"error-card-traceback\">"""
            + "\n".join(card)
            + """</pre>
        </div>
        """
        )
    html = f"""
    <!doctype html>
    <html lang=\"en\">
      <head>
        <title>{error_type}: {error_msg} // {title}</title>
        <style>
          body {{ font-family: monospace; background: #fff; color: #333; }}
          .debugger {{ margin: 2em; max-width: 700px; }}
          .error-card {{
            border: 1px solid #ccc;
            border-radius: 6px;
            margin-bottom: 1em;
            padding: 1em;
            background: #f9f9f9;
            box-shadow: 0 2px 4px rgba(0,0,0,0.03);
            overflow: auto;
          }}
          .error-card-header {{
            font-weight: bold;
            margin-bottom: 0.5em;
            color: #0074d9;
          }}
          .error-card-traceback {{
            max-height: 150px;
            overflow: auto;
            margin: 0;
            white-space: pre-wrap;
          }}
          .plain textarea {{ width: 100%; height: 10em; resize: vertical; overflow: auto; }}
          h1 {{ color: #c00; }}
        </style>
      </head>
      <body style=\"padding-bottom:10px\">
        <div class=\"debugger\">
          <h1>{error_type}</h1>
          <div class=\"detail\">
            <p class=\"errormsg\">{error_type}: {error_msg}</p>
          </div>
          <h2 class=\"traceback\">Traceback <em>(most recent call last)</em></h2>
          {cards_html}
          <blockquote>{error_type}: {error_msg}</blockquote>
          <div class=\"plain\">
            <p>This is the Copy/Paste friendly version of the traceback.</p>
            <textarea readonly>{formatted_tb}</textarea>
          </div>
          <div class=\"explanation\">
            The debugger caught an exception in your ASGI application. You can now
            look at the traceback which led to the error.
          </div>
          <div class=\"footer\">
            Brought to you by <strong class=\"arthur\">DON'T PANIC</strong>, your
            friendly {backend} powered traceback interpreter.
          </div>
        </div>
      </body>
    </html>
    """
    return html
