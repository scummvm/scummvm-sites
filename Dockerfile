FROM rails:4.2.6
MAINTAINER Alex Bevilacqua <alex@alexbevi.com>
RUN mkdir -p /var/app
COPY Gemfile /var/app/Gemfile
WORKDIR /var/app
RUN bundle install
CMD rails s -b 0.0.0.0
