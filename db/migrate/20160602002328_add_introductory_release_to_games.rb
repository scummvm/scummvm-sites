class AddIntroductoryReleaseToGames < ActiveRecord::Migration
  def change
    add_column :games, :introductory_release_id, :integer
  end
end
