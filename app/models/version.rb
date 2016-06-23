class Version < ActiveRecord::Base
  include PublicActivity::Model
  tracked only: [:create], owner: Proc.new { |controller, model| controller.current_user }

  belongs_to :language
  belongs_to :platform
  belongs_to :game
  belongs_to :release, foreign_key: 'introductory_release_id'
  has_many :tests

  def name
    value = "#{platform.name}"
    value += " / #{aliases}" unless aliases.blank?
    value
  end
end
