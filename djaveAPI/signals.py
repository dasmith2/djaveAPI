from django import dispatch


publishable_post_save = dispatch.Signal(providing_args=['instance'])
