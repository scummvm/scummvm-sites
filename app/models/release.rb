class Release < ActiveRecord::Base
  has_many :games
  has_many :engines
  include PublicActivity::Model
  tracked only: [:create], owner: Proc.new { |controller, model| controller.current_user }

  validates :major, uniqueness: { scope: [:minor, :patch] }
  validates :release_date, presence: true

  default_scope { order(release_date: :desc) }

  def name
    "#{major}.#{minor}.#{patch}"
  end
end
