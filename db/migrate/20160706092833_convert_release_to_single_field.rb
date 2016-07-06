class ConvertReleaseToSingleField < ActiveRecord::Migration
  def up
    add_column :releases, :name, :string
    Release.find_each do |release|
      release.name = "#{release.major}.#{release.minor}.#{release.patch}"
      release.save!
    end
    remove_column :releases, :major
    remove_column :releases, :minor
    remove_column :releases, :patch
  end

  def down
    # FIXME do we care about rollbacks at this point?
  end
end
