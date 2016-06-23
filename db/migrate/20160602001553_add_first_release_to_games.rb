class AddFirstReleaseToGames < ActiveRecord::Migration
  def change
    add_column :games, :first_release, :integer
  end
end
