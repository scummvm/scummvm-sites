class CreateTests < ActiveRecord::Migration
  def change
    create_table :tests do |t|
      t.belongs_to :version, index: true, foreign_key: true
      t.belongs_to :user, index: true, foreign_key: true
      t.integer :compatibility
      t.string :user_system
      t.belongs_to :release, index: true, foreign_key: true
      t.string :release_notes
      t.string :comment

      t.timestamps null: false
    end
  end
end
