class Engine < ActiveRecord::Base
  has_many :games
  validates :name, uniqueness: true, presence: true

  before_create do
    self.code = self.name.downcase if self.code.blank?
  end

  default_scope { order(name: :asc) }
end
