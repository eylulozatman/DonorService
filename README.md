In the donor service, you can create a new donor or donate for an existing record.

Show request data "fetches" and shows requests from other (Blood Request) services.

The @app.route('/get_requests', methods=['GET']) function is different from showRequest and listens for requests on a scheduled basis. When a suitable donation is found, it sends an e-mail.

2 tables were used. Donor and class AvailableBlood: represents donor people, and AvailableBlood can be thought of as a blood bank.
