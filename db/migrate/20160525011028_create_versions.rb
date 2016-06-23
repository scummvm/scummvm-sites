class CreateVersions < ActiveRecord::Migration
  def change
    create_table :versions do |t|
      t.references :platform
      t.references :game
      t.date :release_date
      t.string :aliases
      t.string :language
      t.integer :introductory_release_id

      t.timestamps null: false
    end
  end
end
