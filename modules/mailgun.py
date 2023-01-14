import requests 
#def send_simple_message():
#    return requests.post(
#        "https://api.mailgun.net/v3/sandbox3e7663cdd6084e9b893781d30401a2c0.mailgun.org/messages",
#        auth=("api", "key-f8760ce0182fbf86bd0cfc1d677d36e4"),
#        data={"from": "Mailgun Sandbox <postmaster@sandbox3e7663cdd6084e9b893781d30401a2c0.mailgun.org>",
#              "to": "Magna <contacto@magna.cl>",
#              "subject": "Hello Magna",
#              "text": "Mailgun Test Api"})
## You can send up to 300 emails/day from this sandbox server.  Next, you should add your own domain so you can send 10,000 emails/month for free.
#send_simple_message()

class Mailgun:

  ##########
  # CONFIG #
  ##########

  method = "api"
  key = ""
  api_url = ""

  ####################
  # NORMAL MAIL SEND #
  ####################

  def send_email(self, text, to, subject):
    return requests.post(
      self.api_url,
      auth = (self.method, self.key),
      data = {
        "from": "",
        "to": to,
        "subject": subject,
        "html": text
        })
      #https://documentation.mailgun.com/api-sending.html#sending
      #http://blog.mailgun.com/transactional-html-email-templates/

  ##################
  # HTML MAIL SEND #
  ##################

  def send_html_email(self, html, to, subject):
    return requests.post(
      self.api_url,
      auth = (self.method, self.key),
      data = {
        "from": "",
        "to": to,
        "subject": subject,
        "html": html
        })
      #https://documentation.mailgun.com/api-sending.html#sending
      #http://blog.mailgun.com/transactional-html-email-templates/

  ############################################
  # WITH ATACHMENT, TEXT AND HTML VERSION #
  ############################################

  def send_complex_message(self, text, html, to, subject, files = []):
    #Files Format Example: [("attachment", open("files/test.jpg")), ("attachment", open("files/test.txt"))]

    return requests.post(
      self.api_url,
      auth = (self.method, self.key),
      files = files,
      data = {
        "from": "",
        "to": to,
        "subject": subject,
        "html": html,
        "text": text
        })

      #data={
      #  "from": "",
      #  "to": to,
      #  "cc": "",
      #  "bcc": "",
      #  "subject": subject,
      #  "text": text,
      #  "html": html
      #  })
