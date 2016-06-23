class AddNotesToReleases < ActiveRecord::Migration
  def change
    add_column :releases, :notes, :string
  end
end
