class Platform < ActiveRecord::Base
  extend FriendlyId
  friendly_id :name, use: [:slugged, :finders]
end
