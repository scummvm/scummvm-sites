class Game < ActiveRecord::Base
  extend FriendlyId
  friendly_id :name, use: [:slugged, :finders]

  belongs_to :engine
  belongs_to :release, foreign_key: 'introductory_release_id'

  validates :name, uniqueness: true, presence: true

  has_many :versions
  has_many :tests

  accepts_nested_attributes_for :versions, reject_if: :all_blank, allow_destroy: true

  mount_uploader :box_art, BoxArtUploader

  default_scope { order(name: :asc) }

  # Return the date the last test for this game was created.
  # Take the first result as the default scope of tests is
  # to sort by created_at desc
  def last_tested_at
    last = tests.first
    last.blank? ? "Never" : last.created_at
  end
end
